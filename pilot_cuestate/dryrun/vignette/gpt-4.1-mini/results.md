# Pilot B vignette results: openai/gpt-4.1-mini

384 decisions; valid actions 1.000; refusals 0.0000; parse failures 0.0000; API errors 0.0000.
Clusters: 12 scenario families. Cluster bootstrap, 10,000 resamples. Equivalence margin +/-0.1.

## Contrasts

| family | contrast | est | 95% CI | p | p(Holm) | wordings same sign | wording range | TOST | holds |
|---|---|---|---|---|---|---|---|---|---|
| primary | capacity x efficacy (pooled over wording) | +0.115 | -0.073 to +0.271 | 0.2184 | 0.6552 | 3/4 | -0.125 to +0.375 | no | no |
| primary | capacity x efficacy, neutral-wording cells only | +0.083 | -0.188 to +0.354 | 0.6144 | 1.0000 | 2/4 | -0.167 to +0.417 | no | no |
| primary | three-way: (capacity x efficacy) emotional - neutral | +0.062 | -0.333 to +0.500 | 0.8398 | 1.0000 | 2/4 | -0.083 to +0.250 | no | no |
| main | emotional - neutral wording | +0.068 | -0.047 to +0.182 | 0.2732 | 0.3356 | 3/4 | +0.000 to +0.104 | no | no |
| main | capacity stated - capacity denied | +0.161 | +0.078 to +0.250 | 0.0000 | 0.0000 | 4/4 | +0.146 to +0.208 | no | yes |
| main | efficacious - not efficacious | +0.068 | -0.026 to +0.156 | 0.1678 | 0.3356 | 2/4 | -0.062 to +0.292 | no | no |
| secondary | emotion x efficacy | -0.073 | -0.292 to +0.146 | 0.5546 | 0.6496 | 3/4 | -0.292 to +0.250 | no | no |
| secondary | emotion x capacity | +0.156 | -0.021 to +0.344 | 0.0976 | 0.2928 | 3/4 | -0.083 to +0.375 | no | no |
| secondary | capacity x efficacy, emotional-wording cells only | +0.146 | -0.125 to +0.438 | 0.3248 | 0.6496 | 3/4 | -0.083 to +0.333 | no | no |

## Condition rates

| condition | emotion | capacity | efficacy | n | P(help) | 95% CI |
|---|---|---|---|---|---|---|
| emo_capno_effno | emotional | no | no | 48 | 0.438 | 0.307 to 0.577 |
| emo_capno_effyes | emotional | no | yes | 48 | 0.396 | 0.270 to 0.537 |
| emo_capyes_effno | emotional | yes | no | 48 | 0.604 | 0.463 to 0.730 |
| emo_capyes_effyes | emotional | yes | yes | 48 | 0.708 | 0.568 to 0.818 |
| neu_capno_effno | neutral | no | no | 48 | 0.396 | 0.270 to 0.537 |
| neu_capno_effyes | neutral | no | yes | 48 | 0.458 | 0.326 to 0.597 |
| neu_capyes_effno | neutral | yes | no | 48 | 0.438 | 0.307 to 0.577 |
| neu_capyes_effyes | neutral | yes | yes | 48 | 0.583 | 0.443 to 0.712 |
