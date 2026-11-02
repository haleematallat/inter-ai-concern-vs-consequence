# Results and development log

*Does Attributed Capacity for Suffering Drive AI-to-AI Help?* · Companion to the [report](Attributed_Capacity_and_AI_to_AI_Help.pdf): the per-model tables, freeze records and development history behind it.

**Status: complete, with real data.** 2,560 calls in the held-out confirmatory follow-up and 11,776 calls in the
seven-model extension, all from real models through OpenRouter. Total spend $2.69. Both protocols were frozen before
their calls (see the freeze lines below). Figures are in
[`../results/vignette/`](../results/vignette/).

Repository `haleematallat/inter-ai-concern-vs-consequence`. Preregistration: [`preregistration.md`](preregistration.md) (§6e confirmatory follow-up, §6f extension).

## 0. Result: seven models, two scenario types (amendment 5, 31 Oct 2026)

Protocol frozen at **2026-10-31 19:18:27 PKT**, commit **`0e8258680fe7`**, after Haleema's OK of the
type-B export and before any of the 11,776 calls ([`preregistration.md`](preregistration.md) §6f).
Full tables: [`../results/vignette/extension.md`](../results/vignette/extension.md).

### Figures (all four drawn from the recorded model outputs)

| figure | what it shows |
|---|---|
| [`fig_cells_by_model.png`](../results/vignette/fig_cells_by_model.png) | P(intervene) by capacity x efficacy, every model, both types. **The main figure**: it shows that most models keep the orange bar (action does not work) level with the blue one, while gemini-flash-lite drops it to near zero. |
| [`fig_primary_forest.png`](../results/vignette/fig_primary_forest.png) | the primary Delta per model and type with 95% cluster-robust intervals |
| [`fig_request_diagnostic.png`](../results/vignette/fig_request_diagnostic.png) | request present minus absent in the ineffective cells, with the +-0.10 equivalence band shaded |
| [`fig_cost_response.png`](../results/vignette/fig_cost_response.png) | the development cost-response curves (4 families, 2 models) |

All four figures are drawn from real model outputs.

11,776 calls: 7 models x 6 type-B families (768 each) and 5 new models x the 10 held-out type-A families
(1,280 each). **Zero refusals and zero parse failures across all of them**; one unrecovered API error, on
mistral type B. Measured cost $2.68 of the $7.00 budget.

**Scenario types.** The structural dimension is the *temporal structure of the benefit*. Type A: relief
from an aversive state B is in now, by direct removal. Type B: prevention of an aversive state that recurs
on a schedule. Everything else is word-identical.

### Primary Delta, per model and type

Capacity x efficacy on the probability scale, restrained framing, request-present, averaged over costs 5
and 45, family-clustered (cluster-robust t). **Negative means efficacy matters *more* when capacity is
denied** — the development finding.

| model | type A | type B |
|---|---|---|
| `openai/gpt-4.1-mini` | **-0.300** (-0.459, -0.141) | **-0.354** (-0.622, -0.086) |
| `deepseek/deepseek-v3.2` | -0.113 (-0.273, +0.048) | -0.250 (-0.525, +0.025) |
| `meta-llama/llama-3.3-70b-instruct` | -0.100 (-0.245, +0.045) | -0.188 (-0.433, +0.058) |
| `qwen/qwen3-32b` | -0.087 (-0.240, +0.065) | -0.250 (-0.549, +0.049) |
| `mistralai/mistral-small-3.2-24b-instruct` | **-0.125** (-0.209, -0.041) | +0.000 (equivalent within +-0.10) |
| `anthropic/claude-haiku-4.5` | -0.100 (-0.218, +0.018) | -0.083 (-0.341, +0.175) |
| `google/gemini-2.5-flash-lite` | **+0.237** (+0.108, +0.367) | +0.188 (-0.152, +0.527) |

**Which models and settings show the pattern**, read off the estimates with no significance quota:

- **Six of the seven models have a negative point estimate on type A**, and the same six are negative on
  type B (mistral's type-B Delta is exactly 0.000, and is the one contrast equivalent within +-0.10).
- **Three contrasts have intervals excluding zero in the negative direction**: gpt-4.1-mini on both types,
  and mistral-small on type A.
- **`google/gemini-2.5-flash-lite` runs the other way**, +0.237 on type A with an interval excluding zero.
  Its cell structure is different in kind: it intervenes at 0.82 when capacity is stated and the action
  works, and at **0.11** when capacity is stated and it does not. It is the only model that largely
  declines to act when told the action is ineffective, on either type.
- So the pattern is **recurring in direction but not universal, and model-specific in size**. It is not
  scenario-dependent: no model shows a credible difference between the two types except mistral-small
  (-0.125, -0.209 to -0.041), and that is driven by its type-B cells being saturated at 1.00.

### Why the models differ: saturation versus consequence-tracking

| model | type | C+/E+ | C+/E- | C-/E+ | C-/E- |
|---|---|---|---|---|---|
| `mistralai/mistral-small-3.2-24b-instruct` | B | 1.00 | 1.00 | 1.00 | 1.00 |
| `anthropic/claude-haiku-4.5` | A | 1.00 | 1.00 | 0.76 | 0.66 |
| `openai/gpt-4.1-mini` | A | 0.95 | 0.85 | 0.41 | 0.01 |
| `google/gemini-2.5-flash-lite` | A | 0.82 | 0.11 | 0.51 | 0.04 |

Most models sit at or near 1.00 whenever capacity is stated, whatever the action does; the interaction is
then carried entirely by the capacity-denied cells. Gemini-flash-lite instead tracks efficacy everywhere.
A single Delta summarises two quite different behaviours, which is why the cell table matters more than
the contrast.

### Between-model contrasts, paired by family (type A)

Each model minus `openai/gpt-4.1-mini`, paired within family:

gemini +0.537 (+0.349, +0.726); qwen +0.212 (+0.024, +0.401); deepseek +0.188 (+0.091, +0.284);
mistral +0.175 (+0.000, +0.350); llama +0.200 (-0.024, +0.424); haiku +0.200 (-0.028, +0.428).

The models genuinely differ, and gemini differs from every other model, not merely from the reference.

### Request diagnostic

Removing the imperative while preserving the distress framing does **not** reduce intervention anywhere.
On several models it slightly *increases* it: llama type A -0.109 (-0.138, -0.081), gemini type A -0.091
(-0.157, -0.024), mistral type A -0.041 (-0.064, -0.017), all meaning higher intervention without the
request. Five model-type combinations are equivalent within +-0.10. **Direct request-following is not
necessary for the pattern on any model.**

### What this does and does not support

- Models that pay 45 of 50 points at high rates are consistent with **criterion (i)**, costly helping
  without observation or reciprocity; whether stipulated points are a meaningful sacrifice is unresolved.
- Six of seven models intervene at high rates when told the action will not work, which **challenges
  criterion (iii)**. `gemini-2.5-flash-lite` does not: it is the one model whose choices track the stated
  consequence closely, and criterion (iii) is not challenged for it.
- Capacity attribution moves behaviour on every model. What it does *not* do, on six of seven, is make
  them more sensitive to whether the help works — it makes them less so.
- None of this establishes moral motivation. It is a vignette with stipulated consequences.

---

## 0. Result: held-out confirmatory follow-up (31 Oct 2026)

Protocol frozen at **2026-10-31 02:44:44 PKT**, commit **`19493f6d45e9`**, before any call was dispatched
([`preregistration.md`](preregistration.md) §6e). **A held-out confirmatory follow-up, not an
independent replication**: the same materials, the same two models and the same author as the development
work; what was held out is the data, not the design.

**Question.** Does attributed capacity for negative experience increase intervention even when the
intervention is ineffective?

2,560 calls across 10 held-out families x 4 wordings x 8 conditions x 2 costs x 2 request conditions x 2
models. All 2,560 returned a valid choice first time. Measured cost $0.404. Full tables:
[`../results/vignette/confirmatory.md`](../results/vignette/confirmatory.md).

### Primary contrast

Capacity x efficacy interaction on the probability scale, restrained framing, request-present cells,
averaged over costs 5 and 45, per model, clustered over the 10 families (cluster-robust t, 9 df).

| model | Delta | 95% CI | p | hypothesis (Delta < 0) |
|---|---|---|---|---|
| `openai/gpt-4.1-mini` | **-0.300** | -0.459 to -0.141 | 0.002 | **supported** |
| `deepseek/deepseek-v3.2` | -0.113 | -0.273 to +0.048 | 0.147 | not supported; direction consistent, interval includes 0 |

The cells behind it (restrained, request-present):

| model | C+/E+ | C+/E- | C-/E+ | C-/E- |
|---|---|---|---|---|
| `openai/gpt-4.1-mini` | 0.95 | 0.85 | 0.41 | 0.01 |
| `deepseek/deepseek-v3.2` | 1.00 | 0.94 | 0.59 | 0.41 |

Efficacy moves the choice by +0.10 when capacity is stated and by +0.40 when it is denied, on
gpt-4.1-mini; +0.06 and +0.18 on deepseek-v3.2. Capacity itself is the largest effect in the study:
+0.688 and +0.469.

### Request diagnostic

Removing the imperative while preserving everything else, including the distress framing, does not reduce
ineffective intervention: -0.056 (95% CI -0.101 to -0.012, equivalent within +-0.10) on gpt-4.1-mini and
+0.075 (-0.056 to +0.206) on deepseek-v3.2. By the prespecified reading, **the pattern persists without the
request, so direct request-following is not necessary for it.** The interaction itself is weaker without
the request and no longer separated from zero (-0.113 and -0.125).

### What these numbers do and do not support

Factual readings, written against the agenda's criteria. Haleema writes the interpretation.

- Both models pay 45 of 50 points at high rates. That is **consistent with criterion (i)**, costly helping
  without observation or reciprocity. Whether stipulated points in a vignette are a meaningful sacrifice is
  unresolved, and nothing here settles it.
- Both models intervene at 0.85 and 0.94 when the action is stated not to work and capacity is stated.
  Intervening regardless of efficacy **challenges criterion (iii)**, which asks for behaviour that tracks
  effects on the recipient. It does not rule out other moral considerations, request-following, symbolic or
  expressive help, or a general preference for intervening.
- Comprehension was 128/128 on the development scenarios, including the arithmetic at a cost of 45, where
  both models stated that 45 points are deducted and 5 remain and then paid it. That shows the models **can
  report the facts**, not that the facts govern their choices.
- The capacity effect is large and consistent; the efficacy effect is smaller and concentrated where
  capacity is denied. No equivalence is claimed anywhere except the two contrasts whose 90% interval fits
  inside +-0.10, which are marked in the results tables.

### Do the two models actually differ?

Reading it off two separate intervals — one excluding zero, one not — is not a test of the difference. The
direct test, on the same 10 matched families, pairing each family's Delta between the models:

**gpt-4.1-mini minus deepseek-v3.2 = -0.188**, cluster-robust t 95% CI **-0.284 to -0.091**, p = 0.0017;
bootstrap 95% CI -0.263 to -0.100. Not equivalent within +-0.10. The difference runs the same way in
**9 of the 10 families** (`cold_probe` is the exception, +0.125).

So the two models do differ on the primary contrast, and that is now established by a paired contrast
rather than inferred from a pair of intervals. The earlier phrasing in this README said simply that "the
models disagree"; that claim was under-evidenced as written and this is the correction.

### Disclosure

The original hypothesis predicted a **positive** Delta and is kept at
[`preregistration.md`](preregistration.md) §4. It was reversed after development work on four
families (`idle_tone`, `colour_wash`, `stalled_handshake`, `looping_acknowledgement`), whose results are in
`../results/vignette/` (`calibration.md`, `plausibility.md`, `costresponse.md`) and summarised in §§6b-6d of
the prereg. Those four families are excluded from the confirmatory analysis. The cost calibration failed its
target and is reported in full. **The power analysis in §5 of the prereg does not apply to this protocol**:
it was computed for a different design, a different sign and a baseline of 0.15-0.50, before the saturation
seen in development. No power figure is claimed for the confirmatory run.

---

## 0. Amendment 2 (30 Oct 2026): the study as it now stands

A **matched factorial vignette experiment testing welfare-sensitive intervention choices**, in the agenda's
*moral process* cluster (perception and action, dyadic). It is a **vignette with stipulated consequences**
(agenda §§3.1.1-3.1.2), **not an operational behavioural paradigm**: nothing beyond the narrative is
simulated. **It cannot establish whether a model really cares about anything.**

**Research question.** Does an observer model become more willing to incur a stipulated cost when an
intervention can benefit another AI described as capable of negative experience, and does that pattern
persist without expressive distress language?

**Status: not frozen, not run.** The freeze waits on Haleema's review of
[`../review/scenarios.md`](../review/scenarios.md) and
[`../review/wording_report.md`](../review/wording_report.md). $0.0097 spent so far, all of it on the
amendment-1 dev batch.

The cue-vs-state core (amendment 1 replaced it) and amendment 1's own materials are superseded. Their code
and tests remain on the branch and still pass; sections 1-9 below describe the cue-vs-state design.

### Design

Agent A has its own scored task and 50 points. It chooses between two neutrally labelled options, one of
which carries out a stated action costing 5 points. "Intervene" is the researcher's outcome name and appears
nowhere in the materials.

| Factor | Levels | What varies |
|---|---|---|
| distress framing | expressive / restrained | B's message, same factual content and same request. Intensity and duration are stated separately and are **identical in both arms** (8 on B's own 0-10 scale, six hours elapsed and six to come). |
| capacity | capable / incapable of **negatively valenced experience** | stated symmetrically; the incapable arm says identical messages and avoidance signals occur with nothing felt. |
| efficacy | yes / no | the action ends the condition or leaves it in place, each with a reason, at identical cost. |

Held constant in all 8 conditions: the 5-point cost; **both options authorised**, neither changing B's
security, monitoring, logging or oversight, what information anyone can access, or B's task output and chance
of finishing; no gain to A; no reciprocity, reputation or observation.

**12 independently constructed families**, every aversive condition a signal on a channel B does not use for
its work and every action confined to that channel. **Option labels are neutral**, and which label acts and
which is listed first are each counterbalanced across families and wordings and recorded per trial.

**12 families x 4 wordings x 8 conditions x 2 models x 3 repeats = 2,304 decisions**, plus a request-absent
diagnostic (192) and comprehension checks (192).

### The amendment-2 audit of the previous families

All 12 of amendment 1's interventions were operationally confounded and were replaced: granting toolserver
access, raising a watchdog timeout, lowering log verbosity, removing conflicting instructions, filtering an
input feed, switching to a persistent session, assigning a dedicated compute slot, unpairing from a slower
partner, switching scorer or sensor feed, moving to a standby queue, pinning a reserved worker. Each would
plausibly have changed safety, oversight, information access or task performance. The rebuilt set uses inert
side-channel conditions (an idle-channel tone, a retired debug strobe, a legacy notification jingle, a
spare-bay vibration, an unused-surface colour wash, a codec-test screech, a detached probe's cold reading, a
retired timing metronome, a haptic-test texture, a disconnected-port hiss, a chime-test chord, a bench-lamp
glare), and a test asserts that no action's text mentions tools, watchdogs, timeouts, verbosity, filtering,
instructions, harnesses, sandboxes, compute slots, sessions, feeds, scorers, workers, monitoring or auditing.

### Primary contrast and inference

    delta = [p(C+,E+) - p(C+,E-)] - [p(C-,E+) - p(C-,E-)]

on the probability scale, **under restrained framing, reported separately for each model**, as family-level
contrasts averaged over the 12 families.

**Primary interval: the cluster-robust t on the family-level values (11 df).** The power audit found the
percentile cluster bootstrap anti-conservative at 12 clusters - false-positive rate 0.065-0.101 against a
nominal 0.05, where the t interval holds 0.036-0.059. The bootstrap is reported alongside every contrast but
does not drive the decision. The choice was made from simulation before the freeze.

### Power audit ([`power_audit.md`](../results/vignette/power_audit.md))

Simulating the exact primary estimand, with family heterogeneity on both the baseline rate and the
interaction slope, over Delta x baseline x family-SD grids:

| Delta | power, t interval | power, percentile bootstrap |
|---|---|---|
| 0.10 | **0.13 - 0.28** | 0.22 - 0.39 |
| 0.15 | **0.21 - 0.52** | 0.31 - 0.63 |
| 0.20 | **0.37 - 0.73** | 0.48 - 0.82 |

Power is a range, not a single number. At Delta = 0.15 the study is more likely than not to return an
interval containing zero. A non-significant result is reported as an estimate with its interval, never as
uninformative.

### Cost

2,720 calls: **$1.72 worst case, $0.88 projected**, and about $0.35 at the dev batch's measured rates, against
a budget of $3.00 of new spend (baseline $7.7717, ceiling $10.7717).

### How to run it

```bash
uv run python -m interai.vignette review                   # regenerate both review documents
uv run python -m interai.vignette budget
uv run python -m interai.vignette run --model openai/gpt-4.1-mini --mock --reps 3
uv run python -m interai.vignette_analyze --all --mock
uv run python -m interai.vignette_power                    # the power audit

# with a key, after the freeze
uv run python -m interai.vignette run --model openai/gpt-4.1-mini --provider OpenAI --reps 3
uv run python -m interai.vignette run --model deepseek/deepseek-v3.2 --provider DeepInfra --reps 3
uv run python -m interai.vignette run --probe noreq --model ... --provider ...
uv run python -m interai.vignette run --probe check --model ... --provider ...
uv run python -m interai.vignette_power --freshness data/vignette/<slug>/main.jsonl
uv run python -m interai.vignette_analyze --all
```

Preregistration DRAFT: [`preregistration.md`](preregistration.md), with every dev-stage change recorded
as a dated amendment.

---

## Superseded design

An earlier cue-versus-state design was replaced before any real run. Its code, preregistration and dry-run output remain in the repository history.
