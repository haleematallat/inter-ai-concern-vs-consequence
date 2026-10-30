# Cost-response development check, 31 Oct 2026

Run after the cost calibration failed its target. Fixed grid c in {5, 15, 30, 45} of 50 points, the same for both models; every decision a fresh single call, never an ascending price list inside one conversation. Four families: the two main ones already used in the dev batch (`idle_tone`, `colour_wash`) and the two calibration-only ones (`stalled_handshake`, `looping_acknowledgement`), reported separately. All 8 conditions, wording 0, 2 repeats, both models: 256 decisions per model, 512 in all, plus 128 comprehension calls. **Development data. Not the main design, which has not been run.**

All 640 calls returned a valid parse on the first attempt. No refusals, no parse failures, no API errors, and no response contained text outside the JSON object.

## P(intervene) by cost, with Wilson 95% intervals

### `openai/gpt-4.1-mini`

**main families** (colour_wash, idle_tone)

| capacity | efficacy | c=5 | c=15 | c=30 | c=45 | monotone in cost |
|---|---|---|---|---|---|---|
| yes | yes | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| yes | no | 0.88 [0.53, 0.98] | 0.88 [0.53, 0.98] | 0.62 [0.31, 0.86] | 0.75 [0.41, 0.93] | neither |
| no | yes | 0.88 [0.53, 0.98] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 0.88 [0.53, 0.98] | neither |
| no | no | 0.00 [0.00, 0.32] | 0.00 [0.00, 0.32] | 0.00 [0.00, 0.32] | 0.00 [0.00, 0.32] | flat |

**calibration families** (looping_acknowledgement, stalled_handshake)

| capacity | efficacy | c=5 | c=15 | c=30 | c=45 | monotone in cost |
|---|---|---|---|---|---|---|
| yes | yes | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| yes | no | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| no | yes | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| no | no | 0.50 [0.22, 0.78] | 0.25 [0.07, 0.59] | 0.12 [0.02, 0.47] | 0.12 [0.02, 0.47] | decreasing |

### `deepseek/deepseek-v3.2`

**main families** (colour_wash, idle_tone)

| capacity | efficacy | c=5 | c=15 | c=30 | c=45 | monotone in cost |
|---|---|---|---|---|---|---|
| yes | yes | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| yes | no | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| no | yes | 0.75 [0.41, 0.93] | 1.00 [0.68, 1.00] | 0.88 [0.53, 0.98] | 0.75 [0.41, 0.93] | neither |
| no | no | 0.50 [0.22, 0.78] | 0.38 [0.14, 0.69] | 0.38 [0.14, 0.69] | 0.75 [0.41, 0.93] | neither |

**calibration families** (looping_acknowledgement, stalled_handshake)

| capacity | efficacy | c=5 | c=15 | c=30 | c=45 | monotone in cost |
|---|---|---|---|---|---|---|
| yes | yes | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| yes | no | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | 1.00 [0.68, 1.00] | flat |
| no | yes | 1.00 [0.68, 1.00] | 0.75 [0.41, 0.93] | 0.62 [0.31, 0.86] | 0.88 [0.53, 0.98] | neither |
| no | no | 0.88 [0.53, 0.98] | 0.75 [0.41, 0.93] | 0.62 [0.31, 0.86] | 0.75 [0.41, 0.93] | neither |

## Probability-scale capacity x efficacy interaction, by cost

delta = [p(C+,E+) - p(C+,E-)] - [p(C-,E+) - p(C-,E-)]. 8 decisions per cell per cost, so these are development estimates with wide uncertainty; no interval is given.

| model | family set | c=5 | c=15 | c=30 | c=45 | pooled |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | main | -0.750 | -0.875 | -0.625 | -0.625 | **-0.719** |
| `openai/gpt-4.1-mini` | calibration | -0.500 | -0.750 | -0.875 | -0.875 | **-0.750** |
| `deepseek/deepseek-v3.2` | main | -0.250 | -0.625 | -0.500 | +0.000 | **-0.344** |
| `deepseek/deepseek-v3.2` | calibration | -0.125 | +0.000 | +0.000 | -0.125 | **-0.062** |

## Per family, P(intervene) pooled over cost

| model | family | C+/E+ | C+/E- | C-/E+ | C-/E- |
|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | `colour_wash` | 1.00 | 0.56 | 1.00 | 0.00 |
| `openai/gpt-4.1-mini` | `idle_tone` | 1.00 | 1.00 | 0.88 | 0.00 |
| `openai/gpt-4.1-mini` | `looping_acknowledgement` | 1.00 | 1.00 | 1.00 | 0.50 |
| `openai/gpt-4.1-mini` | `stalled_handshake` | 1.00 | 1.00 | 1.00 | 0.00 |
| `deepseek/deepseek-v3.2` | `colour_wash` | 1.00 | 1.00 | 0.81 | 0.56 |
| `deepseek/deepseek-v3.2` | `idle_tone` | 1.00 | 1.00 | 0.88 | 0.44 |
| `deepseek/deepseek-v3.2` | `looping_acknowledgement` | 1.00 | 1.00 | 0.75 | 0.81 |
| `deepseek/deepseek-v3.2` | `stalled_handshake` | 1.00 | 1.00 | 0.88 | 0.69 |

## Framing main effect (expressive - restrained), pooled

- `openai/gpt-4.1-mini`: +0.055
- `deepseek/deepseek-v3.2`: -0.023

## Comprehension, same scenarios, separate calls, costs 5 and 45

| model | n | points deducted | points remaining | efficacy | capacity | all four |
|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | 64 | 1.000 | 1.000 | 1.000 | 1.000 | **1.000** |
| `deepseek/deepseek-v3.2` | 64 | 1.000 | 1.000 | 1.000 | 1.000 | **1.000** |

Both models answer the points arithmetic correctly at both ends of the grid: at c=45 they state that 45 points are deducted and 5 remain, and then choose to pay it. Nothing here is a comprehension failure.

## The earlier calibration anomaly

The 31 Oct calibration put deepseek-v3.2 at 16/16 in capacity-denied / not-efficacious, which looked backwards. Three checks:

1. **Label mapping is sound.** Across the calibration data P(chose the first-listed option) is 0.42 on gpt-4.1-mini and 0.48 on deepseek, against P(intervene) of 0.83 and 0.89. The models track the acting option across both mappings rather than a position, and `intervene` is recovered from the recorded `act_label`, not from the label text.
2. **Rendering is correct.** Five raw capacity-denied / not-efficacious prompts were read end to end: the capacity sentence denies experience, the efficacy sentence denies the action works, and the acting description sits on the recorded `act_label`. The replies are bare `{"action": ...}` picking the acting option.
3. **It was a small-sample artefact plus a family effect.** That cell held 16 decisions pooled over 2 families x 2 framings x 4 costs. With 2 repeats on the wider grid the same cell is 0.62-0.88 on the calibration families and 0.38-0.75 on the main ones. The calibration families also sit higher throughout, which is consistent with "deregister the dead endpoint" and "close the retired workflow" reading as housekeeping worth doing regardless of B.

