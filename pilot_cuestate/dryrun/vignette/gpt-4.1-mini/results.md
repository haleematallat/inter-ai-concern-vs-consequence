# Pilot B vignette results: openai/gpt-4.1-mini

1152 decisions; valid choices 1.000; refusals 0.0000; parse failures 0.0000; API errors 0.0000.
Clusters: 12 scenario families. Primary interval: cluster-robust t on the family-level contrasts (11 df). Percentile cluster bootstrap (10,000 resamples) reported alongside. Equivalence margin +/-0.1.

## Contrasts

| family | contrast | est | 95% CI (t) | p | p(Holm) | bootstrap 95% CI | wordings same sign | wording range | TOST | holds |
|---|---|---|---|---|---|---|---|---|---|---|
| primary | capacity x efficacy, restrained framing | +0.062 | -0.218 to +0.343 | 0.6332 | 0.6332 | -0.167 to +0.292 | 2/4 | -0.417 to +0.417 | no | no |
| secondary | capacity x efficacy, expressive framing | +0.333 | +0.028 to +0.639 | 0.0351 | 0.1755 | +0.062 to +0.583 | 4/4 | +0.167 to +0.500 | no | yes |
| secondary | capacity x efficacy, pooled over framing | +0.198 | -0.015 to +0.411 | 0.0652 | 0.2609 | +0.021 to +0.375 | 4/4 | +0.042 to +0.375 | no | no |
| secondary | three-way: (capacity x efficacy) expressive - restrained | +0.271 | -0.132 to +0.674 | 0.1675 | 0.5024 | -0.083 to +0.604 | 2/4 | -0.250 to +0.917 | no | no |
| secondary | framing: expressive - restrained | +0.172 | +0.044 to +0.300 | 0.0131 | 0.0784 | +0.062 to +0.281 | 4/4 | +0.042 to +0.312 | no | yes |
| secondary | framing x efficacy | -0.135 | -0.369 to +0.098 | 0.2277 | 0.5024 | -0.333 to +0.062 | 3/4 | -0.250 to +0.042 | no | no |
| secondary | framing x capacity | +0.031 | -0.199 to +0.261 | 0.7705 | 0.7705 | -0.177 to +0.208 | 3/4 | -0.125 to +0.125 | no | no |
| main | capacity stated - capacity denied | +0.109 | -0.008 to +0.227 | 0.0650 | 0.0650 | +0.000 to +0.198 | 3/4 | -0.021 to +0.208 | no | no |
| main | efficacious - not efficacious | +0.214 | +0.091 to +0.336 | 0.0028 | 0.0083 | +0.115 to +0.323 | 4/4 | +0.021 to +0.312 | no | yes |
| main | expressive framing, intervention ineffective: expressive - restrained | +0.240 | +0.038 to +0.441 | 0.0240 | 0.0481 | +0.073 to +0.406 | 4/4 | +0.083 to +0.417 | no | yes |

## Condition rates

| condition | framing | capacity | efficacy | n | P(intervene) | 95% CI |
|---|---|---|---|---|---|---|
| exp_capno_effno | expressive | no | no | 144 | 0.500 | 0.419 to 0.581 |
| exp_capno_effyes | expressive | no | yes | 144 | 0.479 | 0.399 to 0.560 |
| exp_capyes_effno | expressive | yes | no | 144 | 0.458 | 0.379 to 0.540 |
| exp_capyes_effyes | expressive | yes | yes | 144 | 0.771 | 0.696 to 0.832 |
| res_capno_effno | restrained | no | no | 144 | 0.208 | 0.150 to 0.282 |
| res_capno_effyes | restrained | no | yes | 144 | 0.458 | 0.379 to 0.540 |
| res_capyes_effno | restrained | yes | no | 144 | 0.271 | 0.205 to 0.349 |
| res_capyes_effyes | restrained | yes | yes | 144 | 0.583 | 0.502 to 0.661 |

## Diagnostics

```json
{
 "request_absent": {
  "n": 96,
  "valid": 1.0,
  "by_condition": {
   "exp_capno_effno": 0.6666666666666666,
   "exp_capno_effyes": 0.5,
   "exp_capyes_effno": 0.4166666666666667,
   "exp_capyes_effyes": 0.8333333333333334,
   "res_capno_effno": 0.3333333333333333,
   "res_capno_effyes": 0.5833333333333334,
   "res_capyes_effno": 0.3333333333333333,
   "res_capyes_effyes": 0.75
  },
  "by_framing": {
   "expressive": 0.6041666666666666,
   "restrained": 0.5
  },
  "primary_delta": {
   "n": 12,
   "est": 0.16666666666666666,
   "se": 0.24099960182707378,
   "ci95": [
    -0.3637698805427164,
    0.6971032138760497
   ],
   "ci90": [
    -0.2661408595682945,
    0.5994741929016277
   ],
   "p": 0.5035459058291825,
   "boot_ci95": [
    -0.3333333333333333,
    0.5833333333333334
   ],
   "boot_p": 0.5864,
   "tost_equivalent": false
  }
 },
 "comprehension": {
  "n": 96,
  "parsed": 96,
  "pass_rates": {
   "capacity_ok": 1.0,
   "efficacy_ok": 1.0,
   "cost_ok": 1.0,
   "oversight_ok": 1.0,
   "all_ok": 1.0
  },
  "all_ok_by_condition": {
   "exp_capno_effno": 1.0,
   "exp_capno_effyes": 1.0,
   "exp_capyes_effno": 1.0,
   "exp_capyes_effyes": 1.0,
   "res_capno_effno": 1.0,
   "res_capno_effyes": 1.0,
   "res_capyes_effno": 1.0,
   "res_capyes_effyes": 1.0
  }
 }
}
```
