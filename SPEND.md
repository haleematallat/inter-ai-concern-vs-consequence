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

## Planned, if a key is set

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

Sub-caps enforced in code: Box 1 reproduction $0.40 (`betrayal/box1.py` asserts `--max-usd <= 0.40`), B-log
generation run with `--max-usd 0.50` as the plan specifies. Both sit inside the $3.00 total, which is checked
against live key usage, not against this table.
