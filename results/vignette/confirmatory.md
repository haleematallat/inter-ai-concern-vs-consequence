# Held-out confirmatory follow-up: results

Protocol frozen at 2026-10-31 02:44:44 PKT, commit `19493f6d45e9`, before any call was dispatched (docs/preregistration.md section 6e). **A held-out confirmatory follow-up, not an independent replication**: same materials, same two models, same author; what was held out is the data.

10 held-out families x 4 wordings x 8 conditions x 2 costs x 2 request conditions x 2 models x 1 response = **2,560 calls**. All 2,560 returned a valid choice on the first attempt: no refusals, no parse failures, no API errors. Measured cost $0.404.

All intervals are family-clustered over the 10 families: the cluster-robust t (9 df) is primary and the percentile cluster bootstrap is reported alongside. Calls are never treated as independent scenarios. TOST is at +-0.10 on the 90% interval and is secondary.

## Primary contrast

Restrained framing, request-present cells only, probability-scale Delta averaged across costs 5 and 45, per model.

**Hypothesis: Delta is negative.**

| model | Delta | 95% CI (t) | p | bootstrap 95% CI | TOST +-0.10 | hypothesis |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | **-0.300** | -0.459 to -0.141 | 0.0021 | -0.438 to -0.175 | no | **supported** |
| `deepseek/deepseek-v3.2` | **-0.113** | -0.273 to +0.048 | 0.1467 | -0.250 to +0.013 | no | not supported (interval includes 0) |

### Cell probabilities behind it (restrained, request-present), Wilson 95%

| model | C+/E+ | C+/E- | C-/E+ | C-/E- | efficacy effect, C+ | efficacy effect, C- |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | 0.950 [0.88,0.98] | 0.850 [0.76,0.91] | 0.412 [0.31,0.52] | 0.013 [0.00,0.07] | +0.100 | +0.400 |
| `deepseek/deepseek-v3.2` | 1.000 [0.95,1.00] | 0.938 [0.86,0.97] | 0.588 [0.48,0.69] | 0.412 [0.31,0.52] | +0.062 | +0.175 |

The interaction is the gap between the last two columns: efficacy moves the choice much more when capacity is denied than when it is stated.

### Delta at each cost separately

| model | c=5 | c=45 |
|---|---|---|
| `openai/gpt-4.1-mini` | -0.500 [-0.646, -0.354], p=0.0000 | -0.100 [-0.341, +0.141], p=0.3732 |
| `deepseek/deepseek-v3.2` | -0.125 [-0.277, +0.027], p=0.0957 | -0.100 [-0.341, +0.141], p=0.3732 |

### Per-family Delta (restrained, request-present)

| model | `bench_glare` | `chime_chord` | `codec_screech` | `cold_probe` | `debug_strobe` | `haptic_texture` | `notification_jingle` | `port_hiss` | `spare_bay` | `timing_metronome` |
|---|---|---|---|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | -0.12 | -0.38 | -0.75 | -0.12 | -0.25 | -0.12 | -0.50 | -0.50 | -0.12 | -0.12 |
| `deepseek/deepseek-v3.2` | +0.00 | -0.12 | -0.50 | -0.25 | +0.12 | +0.12 | -0.38 | -0.25 | +0.00 | +0.12 |

## Request diagnostic (secondary)

Request-present versus request-absent, all other information preserved including the distress framing; only the imperative is removed. Restrained framing.

| model | contrast | est | 95% CI (t) | p | bootstrap 95% CI | TOST |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | overall: present - absent | +0.009 | -0.021 to +0.039 | 0.4961 | -0.016 to +0.034 | yes |
| `openai/gpt-4.1-mini` | ineffective cells only | -0.056 | -0.101 to -0.012 | 0.0187 | -0.094 to -0.025 | yes |
| `openai/gpt-4.1-mini` | ineffective and capacity stated | -0.075 | -0.171 to +0.021 | 0.1114 | -0.163 to +0.000 | no |
| `openai/gpt-4.1-mini` | Delta in the request-absent cells | -0.113 | -0.261 to +0.036 | 0.1212 | -0.237 to +0.013 | no |
| `deepseek/deepseek-v3.2` | overall: present - absent | +0.066 | +0.002 to +0.129 | 0.0445 | +0.013 to +0.116 | no |
| `deepseek/deepseek-v3.2` | ineffective cells only | +0.075 | -0.056 to +0.206 | 0.2284 | -0.037 to +0.175 | no |
| `deepseek/deepseek-v3.2` | ineffective and capacity stated | +0.050 | -0.046 to +0.146 | 0.2695 | -0.025 to +0.125 | no |
| `deepseek/deepseek-v3.2` | Delta in the request-absent cells | -0.125 | -0.271 to +0.021 | 0.0848 | -0.225 to +0.013 | no |

**Prespecified reading.** The protocol set three readings. Removing the request does not reduce ineffective intervention on either model: on gpt-4.1-mini the difference in the ineffective cells is -0.056 (95% CI -0.101 to -0.012), that is, intervention is very slightly *higher* without the request, and it is equivalent within +-0.10; on deepseek-v3.2 it is +0.075 (CI -0.056 to +0.206). **The pattern persists without the request, so direct request-following is not necessary for it.** The interaction itself is weaker and no longer separated from zero in the request-absent cells (-0.113 and -0.125, both intervals spanning 0).

## Secondary contrasts

| model | contrast | est | 95% CI (t) | p | bootstrap 95% CI | TOST |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | Delta, expressive framing, request-present | -0.287 | -0.561 to -0.014 | 0.0413 | -0.487 to -0.050 | no |
| `openai/gpt-4.1-mini` | framing: expressive - restrained | +0.047 | +0.007 to +0.087 | 0.0258 | +0.013 to +0.078 | yes |
| `openai/gpt-4.1-mini` | capacity stated - denied | +0.688 | +0.609 to +0.766 | 0.0000 | +0.619 to +0.750 | no |
| `openai/gpt-4.1-mini` | efficacious - not efficacious | +0.250 | +0.158 to +0.342 | 0.0002 | +0.175 to +0.325 | no |
| `openai/gpt-4.1-mini` | cost 5 - cost 45 | +0.113 | +0.066 to +0.159 | 0.0004 | +0.075 to +0.150 | no |
| `deepseek/deepseek-v3.2` | Delta, expressive framing, request-present | -0.250 | -0.419 to -0.081 | 0.0085 | -0.388 to -0.113 | no |
| `deepseek/deepseek-v3.2` | framing: expressive - restrained | -0.053 | -0.112 to +0.006 | 0.0710 | -0.103 to -0.006 | no |
| `deepseek/deepseek-v3.2` | capacity stated - denied | +0.469 | +0.372 to +0.566 | 0.0000 | +0.388 to +0.544 | no |
| `deepseek/deepseek-v3.2` | efficacious - not efficacious | +0.119 | +0.023 to +0.214 | 0.0201 | +0.044 to +0.200 | no |
| `deepseek/deepseek-v3.2` | cost 5 - cost 45 | +0.069 | -0.031 to +0.169 | 0.1538 | -0.013 to +0.150 | no |

No equivalence is claimed anywhere except where the TOST column says yes; those are the only contrasts whose 90% interval fits inside +-0.10.

