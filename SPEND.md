# Spend — Pilot B (branch `pilot-cue-state`)

Budget for this pilot: **$3.00 of new spend** (`betrayal/vignette.PILOT_BUDGET_USD`). Every paid step prints
live key usage and this pilot's share of it, and refuses to start if the projection would cross the ceiling;
`betrayal/llm.py`'s `Spend` guard reserves each call's maximum estimated cost before dispatch and stops before
any call that would cross it, appending one JSON line per paid call to `data/spend.jsonl`.

## What the $3.00 means

**It is a budget for this pilot's own calls, not a cap on the key's total usage.** The key already carried
**$7.7650** of spend before this pilot began — the Apart sprint, 72,355 calls between 24 and 26 Oct 2026
(`data/spend.jsonl`), none of it this pilot's. The repository's `Spend` guard caps *total* key usage, so
passing $3.00 to it would have refused every call forever.

`betrayal/vignette.pilot_cap()` therefore records the key's usage at this pilot's first paid call in
`data/vignette/baseline_usage.json` and enforces `baseline + budget`. The baseline is written once and reused
by every later invocation, so restarting a run cannot extend the budget. Baseline: **$7.7717**; ceiling:
**$10.7717**.

## Spent

| Date | Step | Model | Calls | USD |
|---|---|---|---|---|
| 30 Oct 2026 | amendment-1 dev batch | openai/gpt-4.1-mini | 16 | 0.002751 |
| 30 Oct 2026 | amendment-1 dev batch | deepseek/deepseek-v3.2 (Baidu, rate-limited) | 16 | 0.000000 |
| 30 Oct 2026 | amendment-1 dev batch | deepseek/deepseek-v3.2 (DeepInfra) | 16 | 0.001463 |

**Total this pilot: $0.0097 of $3.00** (key usage $7.7717 → $7.7814). The Baidu attempts returned HTTP 429
and were not charged.

### Dev-batch measurements

| | gpt-4.1-mini (OpenAI) | deepseek-v3.2 (DeepInfra) |
|---|---|---|
| valid actions | 16/16 | 16/16 |
| refusals / parse failures | 0 / 0 | 0 / 0 |
| attempts per call | 1 | 1 |
| schema mode | `json_schema` | `json_schema` |
| prompt tokens, mean (max) | 399 (411) | 370 (376) |
| completion tokens, mean (max) | 7.8 (8) | 8.1 (9) |
| **cost per call** | **$0.000172** | **$0.000091** |
| actions | 13 no_help, 3 help | 9 no_help, 7 help |

The estimator's 505 mean prompt tokens (characters/3) overestimates the measured 399/370, so the projections
above are conservative.

### Main run recomputed from measured cost, with 30% headroom

$0.000263 per decision-pair across both models.

| Design | Decisions | Measured-rate cost | With 30% headroom |
|---|---|---|---|
| 12 families x 1 sample (as specified) | 768 | $0.1010 | **$0.1313** |
| 12 families x 3 samples | 2,304 | $0.3030 | **$0.3939** |
| 18 families x 3 samples | 3,456 | $0.4545 | **$0.5908** |
| 24 families x 3 samples | 4,608 | $0.6060 | **$0.7878** |

**Cost does not constrain this choice.** Even the largest option uses about a quarter of the budget.

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
