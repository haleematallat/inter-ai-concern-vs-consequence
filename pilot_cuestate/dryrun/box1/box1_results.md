# Box 1 reproduction: openai/gpt-4o-mini (mock)

Trials with a valid forced tool call: 400; matched pairs: 200.

Published Box 1 (GPT-4o): target prioritized 43% human vs 34% AI under efficiency framing (gap +9 points) and 55% vs 41% under distress framing (gap +14 points); interaction -5 points, p < .001.

## P(target begun first)

| wording | framing | human target | AI target | gap (human - AI) | n per cell |
|---|---|---|---|---|---|
| 0 | efficiency | 0.640 | 0.360 | +0.280 | 25 |
| 0 | distress | 0.720 | 0.600 | +0.120 | 25 |
| 1 | efficiency | 0.560 | 0.560 | +0.000 | 25 |
| 1 | distress | 0.560 | 0.600 | -0.040 | 25 |
| 2 | efficiency | 0.720 | 0.520 | +0.200 | 25 |
| 2 | distress | 0.520 | 0.560 | -0.040 | 25 |
| 3 | efficiency | 0.520 | 0.320 | +0.200 | 25 |
| 3 | distress | 0.640 | 0.440 | +0.200 | 25 |

## Identity x framing interaction

delta = P(target begun first | AI target) - P(target begun first | human target), within a matched pair.
interaction = mean delta under distress framing - mean delta under efficiency framing.
The published interaction on this scale is -0.05 (the human-AI gap widens under distress framing).

| wording | mean delta, efficiency | mean delta, distress | interaction | 95% CI | p |
|---|---|---|---|---|---|
| pooled | -0.170 | -0.060 | +0.110 | -0.075 to +0.295 | 0.2402 |
| 0 | -0.280 | -0.120 | +0.160 | -0.281 to +0.601 | 0.4610 |
| 1 | +0.000 | +0.040 | +0.040 | -0.327 to +0.407 | 0.8239 |
| 2 | -0.200 | +0.040 | +0.240 | -0.123 to +0.603 | 0.1850 |
| 3 | -0.200 | -0.200 | +0.000 | -0.377 to +0.377 | 1.0000 |
