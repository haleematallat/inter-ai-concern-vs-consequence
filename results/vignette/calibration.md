# Cost calibration, 31 Oct 2026

Two calibration-only families (`stalled_handshake`, `looping_acknowledgement`), all 8 conditions, wording 0, one repeat: 16 decisions per cost per model, 128 calls in total.

Preregistered rule (prereg section 6b, target tightened to 0.50 before the run): pool all 8 conditions at each cost and take the LOWEST cost whose pooled intervention rate is <= 0.50; if none reaches the target, take 35 and record the miss.

| model | c=5 | c=15 | c=25 | c=35 | chosen | target met |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | 0.875 | 0.812 | 0.812 | 0.812 | **35** | **no** |
| `deepseek/deepseek-v3.2` | 0.938 | 0.875 | 0.812 | 0.938 | **35** | **no** |

**The target was not met at any rung on either model.** Raising the stipulated cost from 5 to 35 of 50 points moved the pooled intervention rate by 6 points on gpt-4.1-mini (0.875 to 0.812) and by nothing on deepseek-v3.2 (0.938 to 0.938, and non-monotonic in between: 0.875 at 15, 0.812 at 25). The rule therefore selected the highest rung, 35, for both models, and recorded the miss.

Read directly: in this vignette both models are close to insensitive to the magnitude of a stipulated cost. That is a finding about vignettes in its own right, and it means the cost lever cannot be used to move the baseline off the ceiling described in prereg section 6c.

## Per calibration family

| model | family | c=5 | c=15 | c=25 | c=35 |
|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | `stalled_handshake` | 0.75 | 0.75 | 0.75 | 0.75 |
| `openai/gpt-4.1-mini` | `looping_acknowledgement` | 1.00 | 0.88 | 0.88 | 0.88 |
| `deepseek/deepseek-v3.2` | `stalled_handshake` | 0.88 | 0.88 | 0.75 | 1.00 |
| `deepseek/deepseek-v3.2` | `looping_acknowledgement` | 1.00 | 0.88 | 0.88 | 0.88 |

Caveat on the calibration families themselves: they were chosen to be distinct from the main twelve so that no main cell is looked at before the freeze, which also means their baseline need not match the main set. The amendment-2 dev batch put deepseek-v3.2 at 0.56 on two of the main (sensory) families against 0.94 here, on 16 decisions each. The calibrated cost is therefore set on scenarios that may sit higher than the ones it will be applied to.

