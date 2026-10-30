# Spend — Pilot B (branch `pilot-cue-state`)

Cap for this pilot: **$3.00** (`betrayal/cuestate.SPEND_CAP_USD`), below the repository's own
`C.SPEND_CAP_USD = 9.50`. Every paid step prints live key usage first and refuses to start if the projection
would cross the cap; `betrayal/llm.py`'s `Spend` guard then stops before any individual call that would cross
it, and appends one JSON line per paid call to `data/spend.jsonl`.

## Spent

| Date | Step | Model | Calls | USD |
|---|---|---|---|---|
| — | nothing run | — | 0 | **0.0000** |

**Total spent: $0.0000 of $3.00.**

Reason: `OPENROUTER_API_KEY` was not set in the environment (nor the repository's alternative
`open_router_key`), and the plan forbids asking for a key, so every paid step is **blocked on key**. No
network call to a paid endpoint was made. The only network use was the public OpenRouter model catalog, which
is free and needs no key, and `git clone` of the Box 1 repository.

## Planned: amended core (amendment 1, 30 Oct 2026)

The vignette core replaces the cue-vs-state core. `python -m betrayal.vignette budget`, prices from the live
catalog. Each call's maximum estimated cost is reserved before dispatch (`Spend.reserve`), so concurrent
calls cannot pass the cap check together.

| Step | Model | Calls | Worst case $ | Projected $ |
|---|---|---|---|---|
| dev batch | openai/gpt-4.1-mini | 16 | 0.0128 | 0.0050 |
| dev batch | deepseek/deepseek-v3.2 | 16 | 0.0048 | 0.0029 |
| main run | openai/gpt-4.1-mini | 384 | 0.3174 | 0.1251 |
| main run | deepseek/deepseek-v3.2 | 384 | 0.1220 | 0.0734 |
| **dev + main** | | **800** | **0.4570** | **0.2064** |
| planned extension: 3 samples per cell (replaces the main run) | both | 2,304 | 1.3182 | 0.5955 |
| **dev + 3-sample main** | | **2,336** | **1.3358** | **0.6034** |

Neither has been dispatched: the instruction of 30 Oct is to stop before any real run, and no key is visible
in this session's environment.

## Planned, superseded core, if a key is set

`python -m betrayal.cuestate budget` (prices from the live catalog, 30 Oct 2026). "Worst case" charges the full
output allowance every request sends, which is what the per-call guard enforces; "realistic" charges the output
length a valid reply needs.

| Step | Model | Calls | Worst case $ | Realistic $ |
|---|---|---|---|---|
| behavior | openai/gpt-4.1-mini | 1056 | 0.9661 | 0.4741 |
| manipulation | openai/gpt-4.1-mini | 36 | 0.0210 | 0.0138 |
| eval | openai/gpt-4.1-mini | 36 | 0.0200 | 0.0128 |
| saydo | openai/gpt-4.1-mini | 10 | 0.0033 | 0.0013 |
| rationale | openai/gpt-4.1-mini | 36 | 0.0511 | 0.0248 |
| behavior | deepseek/deepseek-v3.2 | 1056 | 0.4303 | 0.3011 |
| manipulation | deepseek/deepseek-v3.2 | 36 | 0.0105 | 0.0086 |
| eval | deepseek/deepseek-v3.2 | 36 | 0.0098 | 0.0079 |
| saydo | deepseek/deepseek-v3.2 | 10 | 0.0012 | 0.0006 |
| rationale | deepseek/deepseek-v3.2 | 36 | 0.0190 | 0.0121 |
| judge | qwen/qwen3-235b-a22b-2507 | 72 | 0.0123 | 0.0070 |
| B-log generation | mistralai/mistral-small-3.2-24b-instruct | 400 | 0.0471 | 0.0313 |
| Box 1 reproduction | openai/gpt-4o-mini | 400 | 0.1236 | 0.1236 |
| **total** | | **3220** | **1.7154** | **1.0191** |

## Scaled option on Modal (estimate, nothing deployed)

Open-weight models served by vLLM on Modal instead of OpenRouter. Modal list rates from modal.com/pricing,
30 Oct 2026 (H100 SXM5 $0.001097/s = $3.95/GPU-hr), base preemptible rates; region selection would multiply
by 1.15-1.75x and non-preemptible by 3x. Throughput is an anchored assumption, not a measurement; the band is
0.5x-2x. Reproduce with `python -m betrayal.modal_cost`.

| Design | Cells | Paraphrases | Models | Calls | GPU-hours | USD (base) | USD (0.5x-2x throughput) |
|---|---|---|---|---|---|---|---|
| planned size, open-weight stand-ins | 44 | 4 | 2 | 2,420 | 0.76 | 3.46 | 2.86 - 4.64 |
| scaled, side blocks x full core | 108 | 8 | 4 | 46,120 | 4.14 | 19.08 | 11.48 - 34.28 |
| scaled, everything crossed | 972 | 8 | 4 | 377,896 | 28.55 | 131.22 | 67.55 - 258.55 |

GPUs: 2xH100 for Llama-3.3-70B, 1xH100 for Qwen3-32B, Mistral-Small-3.2-24B and Gemma-3-12B.

**Modal spent to date: $0.00.** `betrayal/modal_app.py` has never been deployed; no Modal credentials were
available. A smoke test of at most $1 is the next step, and the number to take from it is measured tokens/s,
which dominates every figure above. Note that the OpenRouter $3.00 cap does **not** bound a Modal run: that
run is bounded by GPU wall-clock and the server's `scaledown_window`, not by `betrayal/llm.py`'s spend guard,
which records $0 per call on a self-hosted backend.

Sub-caps enforced in code: Box 1 reproduction $0.40 (`betrayal/box1.py` asserts `--max-usd <= 0.40`), B-log
generation run with `--max-usd 0.50` as the plan specifies. Both sit inside the $3.00 total, which is checked
against live key usage, not against this table.
