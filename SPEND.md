# Spend — Pilot B (branch `pilot-cue-state`)

## Two limits, because the key is shared

The OpenRouter key is shared with the sibling pilot session (Pilot A). Two separate limits are enforced, both
in `betrayal/llm.py`'s `Spend` guard, each checked before a call is dispatched and each counting the cost
reserved for calls already in flight:

1. **This pilot's own budget: $3.00**, measured against **this pilot's own ledger spend only**
   (`betrayal/vignette.pilot_spend()` sums the entries in `data/spend.jsonl` whose trial ids belong to this
   study, from this pilot's baseline onwards). A sibling session's spend therefore cannot block this pilot.
2. **A shared ceiling on total key usage: $16.77** — Pilot A's recorded baseline of $7.7745 plus $9.00 of
   combined spend (orchestrator decision, 30 Oct 2026). The two pilots together cannot overshoot the key
   even though neither can block the other.

The key already carried **$7.7650** before this pilot began — the Apart sprint, 72,355 calls between 24 and
26 Oct 2026, none of it this pilot's. This pilot's baseline, written once at its first paid call, is
**$7.7717** (`data/vignette/baseline_usage.json`); the baseline is reused by every later invocation, so
restarting a run cannot extend the budget.

Every paid run prints all of it: live key usage, the baseline, the ceiling, this pilot's own spend and call
count, and how much of the key's rise belongs to other sessions.

## Spent

| Date | Step | Model | Calls | USD |
|---|---|---|---|---|
| 30 Oct 2026 | amendment-1 dev batch | openai/gpt-4.1-mini | 16 | 0.002751 |
| 30 Oct 2026 | amendment-1 dev batch | deepseek/deepseek-v3.2 (Baidu, rate-limited) | 16 | 0.000000 |
| 30 Oct 2026 | amendment-1 dev batch | deepseek/deepseek-v3.2 (DeepInfra) | 16 | 0.001463 |
| 30 Oct 2026 | amendment-2 dev batch | openai/gpt-4.1-mini | 16 | 0.003442 |
| 30 Oct 2026 | amendment-2 dev batch | deepseek/deepseek-v3.2 | 16 | 0.001827 |
| 30 Oct 2026 | comprehension checks | openai/gpt-4.1-mini | 16 | 0.005100 |
| 30 Oct 2026 | comprehension checks | deepseek/deepseek-v3.2 | 16 | 0.002000 |

**Total this pilot: $0.0166 over 96 calls, of $3.00.** The Baidu attempts returned HTTP 429 and were not
charged. Over the same period total key usage rose from $7.7717 to about $8.18, so roughly **$0.39 of the
rise belongs to the sibling session**, not to this pilot — which is why the budget is now enforced on this
pilot's own ledger rather than on the key's total.

### Amendment-2 measured rates

| | gpt-4.1-mini | deepseek-v3.2 |
|---|---|---|
| decision call | $0.000215 | $0.000114 |
| comprehension call | $0.000319 | $0.000125 |
| prompt tokens, mean | 506 | 472 |

At these rates the whole amendment-2 programme (2,720 calls) is about **$0.42**. The two prepared-but-unrun
probes add 128 calibration calls (about $0.02) and 192 plausibility calls (about $0.05).

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

## Planned: amendment-2 programme (30 Oct 2026)

`python -m betrayal.vignette budget`, prices from the live catalog. Each call's maximum estimated cost is
reserved before dispatch (`Spend.reserve`).

| Step | Model | Calls | Worst case $ | Projected $ |
|---|---|---|---|---|
| dev batch | openai/gpt-4.1-mini | 16 | 0.0140 | 0.0063 |
| dev batch | deepseek/deepseek-v3.2 | 16 | 0.0056 | 0.0038 |
| main run, 3 repeats | openai/gpt-4.1-mini | 1,152 | 1.0319 | 0.4620 |
| main run, 3 repeats | deepseek/deepseek-v3.2 | 1,152 | 0.4177 | 0.2766 |
| request-absent diagnostic | openai/gpt-4.1-mini | 96 | 0.0842 | 0.0373 |
| request-absent diagnostic | deepseek/deepseek-v3.2 | 96 | 0.0337 | 0.0223 |
| comprehension checks | openai/gpt-4.1-mini | 96 | 0.0928 | 0.0457 |
| comprehension checks | deepseek/deepseek-v3.2 | 96 | 0.0392 | 0.0277 |
| **total** | | **2,720** | **1.7192** | **0.8818** |

At the dev batch's measured rates ($0.000172 and $0.000091 per call) the whole programme is about **$0.35**.
The amendment-2 prompts are longer than amendment 1's, since every condition now carries the intensity and
authorisation sentences.

Nothing has been dispatched: the freeze waits on Haleema's review of `review/scenarios.md` and
`review/wording_report.md`.

## Planned, superseded amendment-1 core

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
