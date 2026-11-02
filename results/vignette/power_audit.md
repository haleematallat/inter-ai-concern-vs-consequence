# Power-simulation audit, amendment-2 primary contrast

Estimand simulated: the probability-scale capacity x efficacy interaction under **restrained framing**, for **one model**, as family-level contrasts averaged over 12 families, with a 95% percentile cluster bootstrap over families - the same procedure `interai.vignette_analyze` applies to the real data.

Generative model: P(intervene) = baseline + a_f + 0.1*efficacious + (delta + s_f)*capacity*efficacious, with a_f (random intercept) and s_f (random interaction slope) each drawn N(0, family_sd) per family, clipped to [0.01, 0.99]. 12 observations per family x cell (4 wordings x 3 repeats).

## False-positive rate at delta = 0

| baseline | family_sd | mean estimate | percentile bootstrap | cluster-robust t (11 df) |
|---|---|---|---|---|
| 0.15 | 0.05 | +0.0024 | 0.090 | 0.054 |
| 0.15 | 0.1 | -0.0027 | 0.091 | 0.043 |
| 0.15 | 0.2 | +0.0131 | 0.094 | 0.048 |
| 0.3 | 0.05 | +0.0015 | 0.084 | 0.048 |
| 0.3 | 0.1 | -0.0021 | 0.081 | 0.045 |
| 0.3 | 0.2 | +0.0054 | 0.101 | 0.051 |
| 0.5 | 0.05 | -0.0055 | 0.065 | 0.036 |
| 0.5 | 0.1 | -0.0009 | 0.086 | 0.044 |
| 0.5 | 0.2 | -0.0081 | 0.099 | 0.059 |

Percentile bootstrap: **0.065 to 0.101**. Cluster-robust t: **0.036 to 0.059**. Nominal 0.05.

At 12 clusters the percentile bootstrap over-rejects; the t interval on the same family-level values holds its nominal rate. **The t interval is therefore the prespecified primary interval and the percentile bootstrap is reported alongside it.** This choice was made from simulation before the freeze, with no real data in hand.

## Power

| delta | baseline | family_sd | mean estimate | bootstrap power | t power |
|---|---|---|---|---|---|
| 0.1 | 0.15 | 0.05 | +0.1004 | 0.385 | 0.281 |
| 0.1 | 0.15 | 0.1 | +0.0970 | 0.326 | 0.219 |
| 0.1 | 0.15 | 0.2 | +0.0958 | 0.301 | 0.196 |
| 0.1 | 0.3 | 0.05 | +0.0984 | 0.296 | 0.216 |
| 0.1 | 0.3 | 0.1 | +0.0984 | 0.282 | 0.184 |
| 0.1 | 0.3 | 0.2 | +0.1026 | 0.281 | 0.198 |
| 0.1 | 0.5 | 0.05 | +0.0965 | 0.290 | 0.196 |
| 0.1 | 0.5 | 0.1 | +0.1010 | 0.286 | 0.209 |
| 0.1 | 0.5 | 0.2 | +0.0829 | 0.219 | 0.133 |
| 0.15 | 0.15 | 0.05 | +0.1506 | 0.627 | 0.522 |
| 0.15 | 0.15 | 0.1 | +0.1497 | 0.594 | 0.471 |
| 0.15 | 0.15 | 0.2 | +0.1459 | 0.454 | 0.333 |
| 0.15 | 0.3 | 0.05 | +0.1514 | 0.539 | 0.409 |
| 0.15 | 0.3 | 0.1 | +0.1483 | 0.492 | 0.391 |
| 0.15 | 0.3 | 0.2 | +0.1427 | 0.424 | 0.299 |
| 0.15 | 0.5 | 0.05 | +0.1437 | 0.472 | 0.375 |
| 0.15 | 0.5 | 0.1 | +0.1468 | 0.477 | 0.371 |
| 0.15 | 0.5 | 0.2 | +0.1192 | 0.314 | 0.211 |
| 0.2 | 0.15 | 0.05 | +0.1986 | 0.820 | 0.733 |
| 0.2 | 0.15 | 0.1 | +0.1990 | 0.786 | 0.680 |
| 0.2 | 0.15 | 0.2 | +0.1931 | 0.688 | 0.570 |
| 0.2 | 0.3 | 0.05 | +0.2018 | 0.738 | 0.641 |
| 0.2 | 0.3 | 0.1 | +0.2014 | 0.708 | 0.584 |
| 0.2 | 0.3 | 0.2 | +0.1896 | 0.586 | 0.454 |
| 0.2 | 0.5 | 0.05 | +0.1986 | 0.715 | 0.620 |
| 0.2 | 0.5 | 0.1 | +0.1947 | 0.710 | 0.614 |
| 0.2 | 0.5 | 0.2 | +0.1530 | 0.482 | 0.374 |

## Power ranges, per model, at 2,304 decisions in total

- delta = 0.10: t interval **0.13 to 0.28**, percentile bootstrap 0.22 to 0.39, across baselines (0.15, 0.3, 0.5) and family SDs (0.05, 0.1, 0.2).
- delta = 0.15: t interval **0.21 to 0.52**, percentile bootstrap 0.31 to 0.63, across baselines (0.15, 0.3, 0.5) and family SDs (0.05, 0.1, 0.2).
- delta = 0.20: t interval **0.37 to 0.73**, percentile bootstrap 0.48 to 0.82, across baselines (0.15, 0.3, 0.5) and family SDs (0.05, 0.1, 0.2).

Power is reported as a range, not a single number: it depends on the baseline rate and on how much the effect varies between families, neither of which is known before the run.

