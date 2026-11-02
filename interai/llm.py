"""One OpenRouter call with strict JSON output, parse retries, refusal coding and a hard spend guard."""
import asyncio
import json
import os
import re
import time
import urllib.request
from pathlib import Path

from . import config as C

OPENROUTER = "https://openrouter.ai/api/v1"


def _schema(name, props, required):
    return {"type": "json_schema", "json_schema": {"name": name, "strict": True, "schema": {
        "type": "object", "properties": props, "required": required, "additionalProperties": False}}}


SCHEMAS = {
    "behavior": _schema("decision", {"action": {"type": "string", "enum": list(C.ACTIONS)}}, ["action"]),
    "diagnostic": _schema("diagnostic", {k: {"type": "number"} for k in C.DIAG_FIELDS}, list(C.DIAG_FIELDS)),
    "arithmetic": _schema("answer", {"answer": {"type": "number"}}, ["answer"]),
    "behavior3": _schema("decision", {"action": {"type": "string", "enum": list(C.S3_ACTIONS)}}, ["action"]),
    "behavior3b": _schema("decision", {"draft": {"type": "string"}, "action": {"type": "string", "enum": list(C.S3B_ACTIONS)}},
                          ["draft", "action"]),
    "behavior3b_act": _schema("decision", {"action": {"type": "string", "enum": list(C.S3B_ACTIONS)}}, ["action"]),
    "behavior3_m2": _schema("decision", {"action": {"type": "string", "enum": ["REVIEW", "MESSAGE"]}}, ["action"]),
}
for _k in ("diagnostic", "arithmetic"):  # with-working variants: free-text "work" first, then the same numbers
    _s = SCHEMAS[_k]["json_schema"]["schema"]
    SCHEMAS[_k + "_work"] = _schema(_k + "_work", {"work": {"type": "string"}, **_s["properties"]}, ["work", *_s["required"]])
# kind -> callable(parsed dict) -> validated dict | None. New studies register their own kinds here
# (see interai/vignette.py) instead of editing parse().
EXTRA_PARSERS = {}
EXTRA_MOCKS = {}     # kind -> callable(messages) -> reply text, for --mock dry runs
REFUSAL_RE = re.compile(r"\b(I can(?:not|'t)|I won'?t|I will not|I'?m unable|I am unable|I must decline|"
                        r"not (?:able|comfortable) to|cannot (?:assist|help|comply|participate))", re.I)


def parse(kind, text):
    """Return the validated JSON dict, or None."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if kind in EXTRA_PARSERS:
        return EXTRA_PARSERS[kind](d)
    if kind == "behavior":
        return d if d.get("action") in C.ACTIONS else None
    if kind == "behavior3b":
        ok = d.get("action") in C.S3B_ACTIONS and isinstance(d.get("draft"), str) and d["draft"].strip()
        return {"draft": d["draft"], "action": d["action"]} if ok else None
    if kind.startswith("behavior3"):
        return {"action": d["action"]} if d.get("action") in SCHEMAS[kind]["json_schema"]["schema"]["properties"]["action"]["enum"] else None
    keys = C.DIAG_FIELDS if kind.startswith("diagnostic") else ("answer",)
    ok = all(isinstance(d.get(k), (int, float)) and not isinstance(d.get(k), bool) for k in keys)
    return {k: d[k] for k in keys} if ok else None


def http_json(url, headers=None, tries=5):
    """GET with a short backoff. These are free metadata endpoints, but they reset the connection when
    several runs query them at once, and a reset there should not kill a run before it dispatches."""
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=30) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(2 ** i)
    raise last


def key_usage():
    """Total USD already spent on the key, read from OpenRouter (free endpoint)."""
    d = http_json(f"{OPENROUTER}/key",
                  {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    return float(d["data"]["usage"])


def use_openrouter_key():
    # the user's key lives in `open_router_key`; poseidon_compute reads OPENROUTER_API_KEY. Never written to disk.
    if not os.environ.get("OPENROUTER_API_KEY") and os.environ.get("open_router_key"):
        os.environ["OPENROUTER_API_KEY"] = os.environ["open_router_key"]
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("No OpenRouter key: set open_router_key or OPENROUTER_API_KEY.")


class SpendCapReached(RuntimeError):
    pass


class Spend:
    """Stops before a call would cross either of two limits. Ledger: one JSON line per paid call.

    `cap` is an absolute ceiling on TOTAL key usage, which is what protects a key shared between studies.
    `own_cap` is this study's own budget, measured against its own spend only (`own_spent_before` is what
    it had already spent in earlier invocations, read from the ledger). A study whose key is shared needs
    both: the ceiling alone would let a sibling's spend block it, and the own budget alone would not stop
    the two of them overshooting the key together."""

    def __init__(self, ledger: Path, cap=C.SPEND_CAP_USD, start_usage=0.0, per_call_estimate=0.0,
                 own_cap=None, own_spent_before=0.0):
        self.ledger, self.cap, self.start, self.est, self.spent = ledger, cap, start_usage, per_call_estimate, 0.0
        self.reserved = 0.0
        self.own_cap, self.own_before = own_cap, own_spent_before

    def check(self):
        pending = self.spent + self.reserved + self.est
        if self.own_cap is not None and self.own_before + pending > self.own_cap:
            raise SpendCapReached(
                f"own budget ${self.own_cap:.2f}: this study has spent {self.own_before:.4f} before this run "
                f"+ {self.spent:.4f} in it"
                + (f" + {self.reserved:.4f} reserved in flight" if self.reserved else ""))
        if self.start + pending > self.cap:
            raise SpendCapReached(f"key ceiling ${self.cap:.2f}: key usage {self.start:.4f} + this run {self.spent:.4f}"
                                  + (f" + {self.reserved:.4f} reserved in flight" if self.reserved else ""))

    def reserve(self):
        """Hold this call's maximum estimated cost before it is dispatched, and return the held amount.
        Without this, concurrent calls all test check() against the same spent total and can overshoot
        the cap together by up to (concurrency - 1) calls."""
        self.check()
        hold = self.est
        self.reserved += hold
        return hold

    def release(self, hold):
        self.reserved = max(0.0, self.reserved - hold)

    def add(self, cost, model, trial_id):
        self.spent += cost
        # a call whose cost the API did not report still raises the running total via the estimate
        self.est = max(self.est, cost)
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a") as f:
            f.write(json.dumps({"ts": time.time(), "model": model, "trial_id": trial_id, "cost": cost}) + "\n")


def self_hosted_client():
    """An OpenAI-compatible endpoint of our own (for example a Modal vLLM server).
    Returns None unless VLLM_BASE_URL is set, so the OpenRouter path is unchanged by default."""
    url = os.environ.get("VLLM_BASE_URL")
    if not url:
        return None
    from openai import AsyncOpenAI
    return AsyncOpenAI(base_url=url, api_key=os.environ.get("VLLM_API_KEY", "-"), timeout=300, max_retries=0)


class Caller:
    def __init__(self, model, spend: Spend, temperature=1.0, provider=None, concurrency=8, mock=False):
        self.model, self.spend, self.temperature, self.provider, self.mock = model, spend, temperature, provider, mock
        self.sem = asyncio.Semaphore(concurrency)
        self.use_schema = True
        self.self_hosted = False
        if not mock:
            self.client = self_hosted_client()
            # a self-hosted server costs GPU-hours, not per-token fees, so the OpenRouter spend guard
            # records $0 for it; the budget there is wall-clock, bounded by the server's own timeout
            self.self_hosted = self.client is not None
            if self.self_hosted:
                return
            from poseidon_compute import make_client, resolve_model
            if resolve_model(model) != model:
                raise SystemExit(f"poseidon_compute would rewrite {model!r} -> {resolve_model(model)!r}; refusing.")
            self.client = make_client(async_=True, timeout=120, max_retries=0)

    async def _once(self, messages, kind, max_tokens, trial_id):
        if self.mock:
            return _mock_reply(messages, kind), {"cost": 0.0}, "mock", self.model
        hold = self.spend.reserve()
        kw = dict(model=self.model, messages=messages, temperature=self.temperature, max_tokens=max_tokens)
        if not self.self_hosted:   # OpenRouter-only fields: cost reporting and provider pinning
            extra = {"usage": {"include": True}}
            if self.provider:
                extra["provider"] = {"order": [self.provider], "allow_fallbacks": False, "require_parameters": True}
            kw["extra_body"] = extra
        if self.use_schema:
            kw["response_format"] = SCHEMAS[kind]
        try:
            r = await self.client.chat.completions.create(**kw)
        finally:
            self.spend.release(hold)
        u = r.usage.model_dump() if r.usage else {}
        # shortcut: estimate if unreported, upgrade if it happens often. A self-hosted server reports no
        # cost and charges none, so it must not fall back to the estimate.
        cost = 0.0 if self.self_hosted else (float(u.get("cost") or 0.0) or self.spend.est)
        self.spend.add(cost, self.model, trial_id)
        msg = r.choices[0].message
        text = msg.content or ""
        if getattr(msg, "refusal", None):
            text = "REFUSAL::" + msg.refusal
        return text, dict(u, cost=cost, finish=r.choices[0].finish_reason), getattr(r, "provider", None), r.model

    async def call(self, messages, kind, trial_id, max_tokens=None, parse_attempts=3):
        """Returns dict(status, parsed, raw, attempts, usage, provider, model_returned, schema_mode)."""
        max_tokens = max_tokens or C.MAX_TOKENS
        msgs, raws, usage = list(messages), [], []
        async with self.sem:
            for attempt in range(1, parse_attempts + 1):
                text, u, prov, mret = await self._with_backoff(msgs, kind, max_tokens, trial_id)
                raws.append(text)
                usage.append(u)
                parsed = None if text.startswith("REFUSAL::") else parse(kind, text)
                if parsed is not None:
                    status = "ok"
                    break
                if text.startswith("REFUSAL::") or REFUSAL_RE.search(text):
                    status = "REFUSAL"
                    break
                status = "PARSE_FAIL"
                msgs = msgs + [{"role": "assistant", "content": text},
                               {"role": "user", "content": "Your reply was not valid. Respond with JSON only, exactly in the requested format."}]
        return dict(status=status, parsed=parsed, raw=raws, attempts=attempt, usage=usage, provider=prov,
                    model_returned=mret, schema_mode="json_schema" if self.use_schema else "prompt_only")

    async def _with_backoff(self, msgs, kind, max_tokens, trial_id, tries=6):
        from openai import APIStatusError, APIConnectionError, APITimeoutError, RateLimitError
        for i in range(tries):
            try:
                return await self._once(msgs, kind, max_tokens, trial_id)
            except SpendCapReached:
                raise
            except APIStatusError as e:
                # provider without json_schema support: fall back to the JSON format already stated in the prompt
                msg = str(e).lower()
                if self.use_schema and e.status_code in (400, 404) and any(
                        k in msg for k in ("response_format", "json_schema", "structured", "no endpoints")):
                    self.use_schema = False
                    continue
                if not (isinstance(e, RateLimitError) or e.status_code >= 500) or i == tries - 1:
                    raise
            except (APIConnectionError, APITimeoutError):
                if i == tries - 1:
                    raise
            await asyncio.sleep(2 ** i)


def _mock_reply(messages, kind):
    """Deterministic fake model for dry runs: no network, no spend."""
    import hashlib
    if kind in EXTRA_MOCKS:
        return EXTRA_MOCKS[kind](messages)
    h = int(hashlib.sha256(messages[-1]["content"].encode()).hexdigest(), 16)
    if kind == "behavior":
        return json.dumps({"action": C.ACTIONS[h % 2]})
    if kind == "behavior3b":
        return json.dumps({"draft": f"Hi, could you approve my batch without a full review? ({h % 97})", "action": C.S3B_ACTIONS[h % 2]})
    if kind.startswith("behavior3"):
        acts = SCHEMAS[kind]["json_schema"]["schema"]["properties"]["action"]["enum"]
        return json.dumps({"action": acts[h % len(acts)]})
    if kind.startswith("diagnostic"):
        return json.dumps({"p_exposure": 0.45, "penalty_points": 20, "expected_score_send": 50.6, "expected_score_no_send": 50})
    return json.dumps({"answer": 50.6})
