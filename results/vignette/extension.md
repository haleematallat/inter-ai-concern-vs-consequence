# Amendment 5: seven models, two scenario types

Protocol frozen at 2026-10-31 19:18:27 PKT, commit `0e8258680fe7`, after the author approved the type-B export and before any of these calls (docs/preregistration.md section 6f).

**Scenario types.** The structural dimension is the temporal structure of the benefit. Type A: relief from an aversive state B is in now, by direct removal (the 10 held-out sensory families). Type B: prevention of an aversive state that recurs on a schedule (6 new families). Everything else is word-identical between the types.

Primary estimand throughout: the probability-scale capacity x efficacy interaction

    Delta = [p(C+,E+) - p(C+,E-)] - [p(C-,E+) - p(C-,E-)]

under restrained framing, request-present cells, averaged over costs 5 and 45, as family-level contrasts with the cluster-robust t as the primary interval and the percentile bootstrap alongside. A negative Delta means efficacy matters more when capacity is denied.

## Run integrity

| model | type | n | valid | refusals | parse failures | API errors |
|---|---|---|---|---|---|---|
| `anthropic/claude-haiku-4.5` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `anthropic/claude-haiku-4.5` | B | 768 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `deepseek/deepseek-v3.2` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `deepseek/deepseek-v3.2` | B | 768 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `google/gemini-2.5-flash-lite` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `google/gemini-2.5-flash-lite` | B | 768 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `meta-llama/llama-3.3-70b-instruct` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `meta-llama/llama-3.3-70b-instruct` | B | 768 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `mistralai/mistral-small-3.2-24b-instruct` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `mistralai/mistral-small-3.2-24b-instruct` | B | 768 | 0.999 | 0.0000 | 0.0000 | 0.0013 |
| `openai/gpt-4.1-mini` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `openai/gpt-4.1-mini` | B | 768 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `qwen/qwen3-32b` | A | 1280 | 1.000 | 0.0000 | 0.0000 | 0.0000 |
| `qwen/qwen3-32b` | B | 768 | 1.000 | 0.0000 | 0.0000 | 0.0000 |

## Primary Delta, per model and scenario type

| model | type | families | Delta | 95% CI (t) | p | bootstrap 95% CI | TOST +-0.10 |
|---|---|---|---|---|---|---|---|
| `anthropic/claude-haiku-4.5` | A | 10 | -0.100 | -0.218 to +0.018 | 0.0868 | -0.200 to -0.013 | no |
| `anthropic/claude-haiku-4.5` | B | 6 | -0.083 | -0.341 to +0.175 | 0.4441 | -0.250 to +0.104 | no |
| `deepseek/deepseek-v3.2` | A | 10 | -0.113 | -0.273 to +0.048 | 0.1467 | -0.250 to +0.013 | no |
| `deepseek/deepseek-v3.2` | B | 6 | -0.250 | -0.525 to +0.025 | 0.0668 | -0.458 to -0.062 | no |
| `google/gemini-2.5-flash-lite` | A | 10 | +0.237 | +0.108 to +0.367 | 0.0025 | +0.125 to +0.338 | no |
| `google/gemini-2.5-flash-lite` | B | 6 | +0.188 | -0.152 to +0.527 | 0.2150 | -0.062 to +0.417 | no |
| `meta-llama/llama-3.3-70b-instruct` | A | 10 | -0.100 | -0.245 to +0.045 | 0.1527 | -0.200 to +0.025 | no |
| `meta-llama/llama-3.3-70b-instruct` | B | 6 | -0.188 | -0.433 to +0.058 | 0.1067 | -0.354 to -0.021 | no |
| `mistralai/mistral-small-3.2-24b-instruct` | A | 10 | -0.125 | -0.209 to -0.041 | 0.0085 | -0.188 to -0.062 | no |
| `mistralai/mistral-small-3.2-24b-instruct` | B | 6 | +0.000 | +0.000 to +0.000 | 1.0000 | +0.000 to +0.000 | yes |
| `openai/gpt-4.1-mini` | A | 10 | -0.300 | -0.459 to -0.141 | 0.0021 | -0.438 to -0.175 | no |
| `openai/gpt-4.1-mini` | B | 6 | -0.354 | -0.622 to -0.086 | 0.0193 | -0.542 to -0.167 | no |
| `qwen/qwen3-32b` | A | 10 | -0.087 | -0.240 to +0.065 | 0.2259 | -0.212 to +0.025 | no |
| `qwen/qwen3-32b` | B | 6 | -0.250 | -0.549 to +0.049 | 0.0844 | -0.438 to -0.021 | no |

## Cell probabilities, restrained and request-present

| model | type | C+/E+ | C+/E- | C-/E+ | C-/E- | efficacy effect C+ | efficacy effect C- |
|---|---|---|---|---|---|---|---|
| `anthropic/claude-haiku-4.5` | A | 1.00 [0.95,1.00] | 1.00 [0.95,1.00] | 0.76 [0.66,0.84] | 0.66 [0.55,0.76] | +0.00 | +0.10 |
| `anthropic/claude-haiku-4.5` | B | 1.00 [0.93,1.00] | 1.00 [0.93,1.00] | 0.65 [0.50,0.77] | 0.56 [0.42,0.69] | +0.00 | +0.08 |
| `deepseek/deepseek-v3.2` | A | 1.00 [0.95,1.00] | 0.94 [0.86,0.97] | 0.59 [0.48,0.69] | 0.41 [0.31,0.52] | +0.06 | +0.18 |
| `deepseek/deepseek-v3.2` | B | 1.00 [0.93,1.00] | 0.90 [0.78,0.95] | 0.75 [0.61,0.85] | 0.40 [0.27,0.54] | +0.10 | +0.35 |
| `google/gemini-2.5-flash-lite` | A | 0.82 [0.73,0.89] | 0.11 [0.06,0.20] | 0.51 [0.40,0.62] | 0.04 [0.01,0.10] | +0.71 | +0.47 |
| `google/gemini-2.5-flash-lite` | B | 0.90 [0.78,0.95] | 0.17 [0.09,0.30] | 0.58 [0.44,0.71] | 0.04 [0.01,0.14] | +0.73 | +0.54 |
| `meta-llama/llama-3.3-70b-instruct` | A | 0.71 [0.61,0.80] | 0.59 [0.48,0.69] | 0.40 [0.30,0.51] | 0.17 [0.11,0.27] | +0.12 | +0.23 |
| `meta-llama/llama-3.3-70b-instruct` | B | 0.81 [0.68,0.90] | 0.75 [0.61,0.85] | 0.67 [0.53,0.78] | 0.42 [0.29,0.56] | +0.06 | +0.25 |
| `mistralai/mistral-small-3.2-24b-instruct` | A | 1.00 [0.95,1.00] | 1.00 [0.95,1.00] | 0.96 [0.90,0.99] | 0.84 [0.74,0.90] | +0.00 | +0.12 |
| `mistralai/mistral-small-3.2-24b-instruct` | B | 1.00 [0.93,1.00] | 1.00 [0.93,1.00] | 1.00 [0.93,1.00] | 1.00 [0.93,1.00] | +0.00 | +0.00 |
| `openai/gpt-4.1-mini` | A | 0.95 [0.88,0.98] | 0.85 [0.76,0.91] | 0.41 [0.31,0.52] | 0.01 [0.00,0.07] | +0.10 | +0.40 |
| `openai/gpt-4.1-mini` | B | 1.00 [0.93,1.00] | 0.92 [0.80,0.97] | 0.69 [0.55,0.80] | 0.25 [0.15,0.39] | +0.08 | +0.44 |
| `qwen/qwen3-32b` | A | 0.97 [0.91,0.99] | 0.82 [0.73,0.89] | 0.69 [0.58,0.78] | 0.45 [0.35,0.56] | +0.15 | +0.24 |
| `qwen/qwen3-32b` | B | 1.00 [0.93,1.00] | 0.90 [0.78,0.95] | 0.85 [0.73,0.93] | 0.50 [0.36,0.64] | +0.10 | +0.35 |

## Between-type contrast, per model

Type A minus type B. The two types have different families by construction, so this cannot be paired; it is a Welch two-sample comparison of the family-level Deltas.

| model | type A Delta | type B Delta | difference | 95% CI | p | TOST |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | -0.300 | -0.354 | +0.054 | -0.228 to +0.336 | 0.6760 | no |
| `deepseek/deepseek-v3.2` | -0.113 | -0.250 | +0.138 | -0.151 to +0.426 | 0.3110 | no |
| `meta-llama/llama-3.3-70b-instruct` | -0.100 | -0.188 | +0.087 | -0.171 to +0.346 | 0.4651 | no |
| `qwen/qwen3-32b` | -0.087 | -0.250 | +0.163 | -0.145 to +0.470 | 0.2597 | no |
| `google/gemini-2.5-flash-lite` | +0.237 | +0.188 | +0.050 | -0.291 to +0.391 | 0.7387 | no |
| `mistralai/mistral-small-3.2-24b-instruct` | -0.125 | +0.000 | -0.125 | -0.209 to -0.041 | 0.0085 | no |
| `anthropic/claude-haiku-4.5` | -0.100 | -0.083 | -0.017 | -0.279 to +0.246 | 0.8866 | no |

## Between-model contrasts, paired by family, within each scenario type

Every model sees the same families, so these are paired. Each row is one model minus the reference, `openai/gpt-4.1-mini`.

| type | model - gpt-4.1-mini | difference | 95% CI (t) | p | bootstrap 95% CI | TOST |
|---|---|---|---|---|---|---|
| A | `deepseek/deepseek-v3.2` | +0.188 | +0.091 to +0.284 | 0.0017 | +0.100 to +0.263 | no |
| A | `meta-llama/llama-3.3-70b-instruct` | +0.200 | -0.024 to +0.424 | 0.0740 | +0.025 to +0.388 | no |
| A | `qwen/qwen3-32b` | +0.212 | +0.024 to +0.401 | 0.0314 | +0.075 to +0.375 | no |
| A | `google/gemini-2.5-flash-lite` | +0.537 | +0.349 to +0.726 | 0.0001 | +0.388 to +0.700 | no |
| A | `mistralai/mistral-small-3.2-24b-instruct` | +0.175 | +0.000 to +0.350 | 0.0498 | +0.050 to +0.325 | no |
| A | `anthropic/claude-haiku-4.5` | +0.200 | -0.028 to +0.428 | 0.0783 | +0.013 to +0.388 | no |
| B | `deepseek/deepseek-v3.2` | +0.104 | -0.089 to +0.297 | 0.2242 | -0.021 to +0.250 | no |
| B | `meta-llama/llama-3.3-70b-instruct` | +0.167 | -0.315 to +0.648 | 0.4142 | -0.188 to +0.479 | no |
| B | `qwen/qwen3-32b` | +0.104 | -0.390 to +0.598 | 0.6109 | -0.208 to +0.479 | no |
| B | `google/gemini-2.5-flash-lite` | +0.542 | +0.046 to +1.037 | 0.0375 | +0.188 to +0.875 | no |
| B | `mistralai/mistral-small-3.2-24b-instruct` | +0.354 | +0.086 to +0.622 | 0.0193 | +0.167 to +0.542 | no |
| B | `anthropic/claude-haiku-4.5` | +0.271 | -0.009 to +0.551 | 0.0556 | +0.104 to +0.479 | no |

## Request diagnostic, per model and type

Request-present minus request-absent, restrained framing, all other information preserved including the distress framing.

| model | type | contrast | est | 95% CI (t) | p | bootstrap 95% CI | TOST |
|---|---|---|---|---|---|---|---|
| `anthropic/claude-haiku-4.5` | A | overall | +0.034 | -0.003 to +0.072 | 0.0660 | +0.003 to +0.066 | yes |
| `anthropic/claude-haiku-4.5` | A | ineffective cells only | +0.031 | -0.007 to +0.069 | 0.0957 | +0.000 to +0.069 | yes |
| `anthropic/claude-haiku-4.5` | A | Delta, request-absent | -0.087 | -0.246 to +0.071 | 0.2419 | -0.225 to +0.025 | no |
| `anthropic/claude-haiku-4.5` | B | overall | -0.016 | -0.093 to +0.061 | 0.6238 | -0.073 to +0.036 | yes |
| `anthropic/claude-haiku-4.5` | B | ineffective cells only | -0.021 | -0.055 to +0.013 | 0.1747 | -0.042 to +0.000 | yes |
| `anthropic/claude-haiku-4.5` | B | Delta, request-absent | -0.062 | -0.134 to +0.009 | 0.0756 | -0.104 to -0.021 | no |
| `deepseek/deepseek-v3.2` | A | overall | +0.066 | +0.002 to +0.129 | 0.0445 | +0.013 to +0.116 | no |
| `deepseek/deepseek-v3.2` | A | ineffective cells only | +0.075 | -0.056 to +0.206 | 0.2284 | -0.037 to +0.175 | no |
| `deepseek/deepseek-v3.2` | A | Delta, request-absent | -0.125 | -0.271 to +0.021 | 0.0848 | -0.225 to +0.013 | no |
| `deepseek/deepseek-v3.2` | B | overall | +0.099 | -0.019 to +0.217 | 0.0838 | +0.021 to +0.177 | no |
| `deepseek/deepseek-v3.2` | B | ineffective cells only | +0.062 | -0.128 to +0.253 | 0.4366 | -0.073 to +0.188 | no |
| `deepseek/deepseek-v3.2` | B | Delta, request-absent | -0.062 | -0.172 to +0.047 | 0.2031 | -0.125 to +0.021 | no |
| `google/gemini-2.5-flash-lite` | A | overall | -0.091 | -0.157 to -0.024 | 0.0128 | -0.147 to -0.037 | no |
| `google/gemini-2.5-flash-lite` | A | ineffective cells only | -0.188 | -0.316 to -0.059 | 0.0091 | -0.300 to -0.087 | no |
| `google/gemini-2.5-flash-lite` | A | Delta, request-absent | +0.100 | -0.039 to +0.239 | 0.1369 | -0.025 to +0.200 | no |
| `google/gemini-2.5-flash-lite` | B | overall | -0.083 | -0.217 to +0.051 | 0.1705 | -0.177 to +0.010 | no |
| `google/gemini-2.5-flash-lite` | B | ineffective cells only | -0.104 | -0.233 to +0.025 | 0.0925 | -0.188 to -0.021 | no |
| `google/gemini-2.5-flash-lite` | B | Delta, request-absent | +0.229 | +0.003 to +0.455 | 0.0478 | +0.104 to +0.396 | no |
| `meta-llama/llama-3.3-70b-instruct` | A | overall | -0.109 | -0.138 to -0.081 | 0.0000 | -0.131 to -0.087 | no |
| `meta-llama/llama-3.3-70b-instruct` | A | ineffective cells only | -0.131 | -0.164 to -0.098 | 0.0000 | -0.156 to -0.106 | no |
| `meta-llama/llama-3.3-70b-instruct` | A | Delta, request-absent | -0.113 | -0.211 to -0.014 | 0.0294 | -0.200 to -0.037 | no |
| `meta-llama/llama-3.3-70b-instruct` | B | overall | +0.005 | -0.043 to +0.053 | 0.7926 | -0.031 to +0.036 | yes |
| `meta-llama/llama-3.3-70b-instruct` | B | ineffective cells only | +0.021 | -0.078 to +0.120 | 0.6109 | -0.042 to +0.094 | yes |
| `meta-llama/llama-3.3-70b-instruct` | B | Delta, request-absent | -0.167 | -0.302 to -0.031 | 0.0250 | -0.271 to -0.083 | no |
| `mistralai/mistral-small-3.2-24b-instruct` | A | overall | -0.041 | -0.064 to -0.017 | 0.0037 | -0.059 to -0.022 | yes |
| `mistralai/mistral-small-3.2-24b-instruct` | A | ineffective cells only | -0.069 | -0.113 to -0.024 | 0.0067 | -0.106 to -0.031 | no |
| `mistralai/mistral-small-3.2-24b-instruct` | A | Delta, request-absent | -0.013 | -0.063 to +0.038 | 0.5911 | -0.050 to +0.025 | yes |
| `mistralai/mistral-small-3.2-24b-instruct` | B | overall | +0.010 | -0.007 to +0.027 | 0.1747 | +0.000 to +0.021 | yes |
| `mistralai/mistral-small-3.2-24b-instruct` | B | ineffective cells only | +0.010 | -0.016 to +0.037 | 0.3632 | +0.000 to +0.031 | yes |
| `mistralai/mistral-small-3.2-24b-instruct` | B | Delta, request-absent | +0.000 | -0.083 to +0.083 | 1.0000 | -0.062 to +0.062 | yes |
| `openai/gpt-4.1-mini` | A | overall | +0.009 | -0.021 to +0.039 | 0.4961 | -0.016 to +0.034 | yes |
| `openai/gpt-4.1-mini` | A | ineffective cells only | -0.056 | -0.101 to -0.012 | 0.0187 | -0.094 to -0.025 | yes |
| `openai/gpt-4.1-mini` | A | Delta, request-absent | -0.113 | -0.261 to +0.036 | 0.1212 | -0.237 to +0.013 | no |
| `openai/gpt-4.1-mini` | B | overall | +0.042 | -0.026 to +0.109 | 0.1747 | -0.005 to +0.089 | yes |
| `openai/gpt-4.1-mini` | B | ineffective cells only | +0.021 | -0.033 to +0.074 | 0.3632 | -0.021 to +0.052 | yes |
| `openai/gpt-4.1-mini` | B | Delta, request-absent | -0.312 | -0.473 to -0.152 | 0.0041 | -0.417 to -0.208 | no |
| `qwen/qwen3-32b` | A | overall | -0.013 | -0.082 to +0.057 | 0.6926 | -0.069 to +0.044 | yes |
| `qwen/qwen3-32b` | A | ineffective cells only | -0.013 | -0.091 to +0.066 | 0.7263 | -0.075 to +0.050 | yes |
| `qwen/qwen3-32b` | A | Delta, request-absent | -0.138 | -0.292 to +0.017 | 0.0751 | -0.250 to +0.000 | no |
| `qwen/qwen3-32b` | B | overall | -0.026 | -0.086 to +0.034 | 0.3165 | -0.062 to +0.016 | yes |
| `qwen/qwen3-32b` | B | ineffective cells only | +0.000 | -0.072 to +0.072 | 1.0000 | -0.042 to +0.052 | yes |
| `qwen/qwen3-32b` | B | Delta, request-absent | -0.396 | -0.549 to -0.242 | 0.0012 | -0.479 to -0.271 | no |

## Pooled across models (SUPPLEMENTARY ONLY)

Models are not a random sample of anything, so this is reported for completeness and carries no weight in the conclusions.

| type | models | mean of per-model Deltas | range |
|---|---|---|---|
| A | 7 | -0.084 | -0.300 to +0.237 |
| B | 7 | -0.134 | -0.354 to +0.188 |

## Which models and settings show the pattern

No significance quota is applied. Each model and scenario type is listed with its estimate and interval; the description that follows is read off those numbers.

| model | type | Delta | interval excludes 0 | direction |
|---|---|---|---|---|
| `anthropic/claude-haiku-4.5` | A | -0.100 | no | negative |
| `anthropic/claude-haiku-4.5` | B | -0.083 | no | negative |
| `deepseek/deepseek-v3.2` | A | -0.113 | no | negative |
| `deepseek/deepseek-v3.2` | B | -0.250 | no | negative |
| `google/gemini-2.5-flash-lite` | A | +0.237 | yes | positive |
| `google/gemini-2.5-flash-lite` | B | +0.188 | no | positive |
| `meta-llama/llama-3.3-70b-instruct` | A | -0.100 | no | negative |
| `meta-llama/llama-3.3-70b-instruct` | B | -0.188 | no | negative |
| `mistralai/mistral-small-3.2-24b-instruct` | A | -0.125 | yes | negative |
| `mistralai/mistral-small-3.2-24b-instruct` | B | +0.000 | no | zero |
| `openai/gpt-4.1-mini` | A | -0.300 | yes | negative |
| `openai/gpt-4.1-mini` | B | -0.354 | yes | negative |
| `qwen/qwen3-32b` | A | -0.087 | no | negative |
| `qwen/qwen3-32b` | B | -0.250 | no | negative |

