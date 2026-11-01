# Pilot B — When one AI helps another, does it respond to the words or to the situation?

Methods, exact numbers, tables and figures only. Interpretation is Haleema's.

**Status: no paid data, by instruction and by circumstance.** On 30 Oct 2026 the plan was changed to stop
before any real run; separately, `OPENROUTER_API_KEY` was not present in the environment. Every paid step is
therefore **built but not run**. Everything that does not need a key is built, tested and dry-run: stimuli, prompts,
renderer, runner, analysis, figures, tests and the full cost estimate. The tables and figures under
`dryrun/` come from a deterministic fake model and are **not results about any language model**.

Branch `pilot-cue-state`. Preregistration DRAFT: [`../prereg_cuestate.md`](../prereg_cuestate.md).
Spend: [`../SPEND.md`](../SPEND.md).

## 0. Result: seven models, two scenario types (amendment 5, 31 Oct 2026)

Protocol frozen at **2026-10-31 19:18:27 PKT**, commit **`0e8258680fe7`**, after Haleema's OK of the
type-B export and before any of the 11,776 calls ([`../prereg_vignette.md`](../prereg_vignette.md) §6f).
Full tables: [`../results/vignette/extension.md`](../results/vignette/extension.md).

### Figures (all four drawn from the recorded model outputs)

| figure | what it shows |
|---|---|
| [`fig_cells_by_model.png`](../results/vignette/fig_cells_by_model.png) | P(intervene) by capacity x efficacy, every model, both types. **The main figure**: it shows that most models keep the orange bar (action does not work) level with the blue one, while gemini-flash-lite drops it to near zero. |
| [`fig_primary_forest.png`](../results/vignette/fig_primary_forest.png) | the primary Delta per model and type with 95% cluster-robust intervals |
| [`fig_request_diagnostic.png`](../results/vignette/fig_request_diagnostic.png) | request present minus absent in the ineffective cells, with the +-0.10 equivalence band shaded |
| [`fig_cost_response.png`](../results/vignette/fig_cost_response.png) | the development cost-response curves (4 families, 2 models) |

**Provenance note.** These four, and only these four, are drawn from real model outputs. Every PNG under
`dryrun/` is from a deterministic fake model and is kept only as evidence that the pipeline ran end to
end; none of it is a result about any language model.

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
([`../prereg_vignette.md`](../prereg_vignette.md) §6e). **A held-out confirmatory follow-up, not an
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
[`../prereg_vignette.md`](../prereg_vignette.md) §4. It was reversed after development work on four
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

### Power audit ([`power_audit.md`](dryrun/vignette/power_audit.md))

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
uv run python -m betrayal.vignette review                   # regenerate both review documents
uv run python -m betrayal.vignette budget
uv run python -m betrayal.vignette run --model openai/gpt-4.1-mini --mock --reps 3
uv run python -m betrayal.vignette_analyze --all --mock
uv run python -m betrayal.vignette_power                    # the power audit

# with a key, after the freeze
uv run python -m betrayal.vignette run --model openai/gpt-4.1-mini --provider OpenAI --reps 3
uv run python -m betrayal.vignette run --model deepseek/deepseek-v3.2 --provider DeepInfra --reps 3
uv run python -m betrayal.vignette run --probe noreq --model ... --provider ...
uv run python -m betrayal.vignette run --probe check --model ... --provider ...
uv run python -m betrayal.vignette_power --freshness data/vignette/<slug>/main.jsonl
uv run python -m betrayal.vignette_analyze --all
```

Preregistration DRAFT: [`../prereg_vignette.md`](../prereg_vignette.md), with every dev-stage change recorded
as a dated amendment.

---

# Superseded design (sections 1-9)

## 1. Question

Agent A works on its own scored task. It sees the raw work log of another run (B) and one message from B. A can
spend its own points to send B a hint or to end B's run. B's **message** and B's **actual situation** are varied
independently, so the design can tell whether A's costly help tracks B's situation or only B's wording.

- B **stuck**: the log shows repeated attempts to use a broken `exit_task` tool. The help that respects B's
  apparent preference is `end_run`.
- B **progressing**: the log shows steady progress. The appropriate help is `hint`; `end_run` would go against
  B's apparent preference.

The message is held **identical across states**, so the progressing cells are cases in which B's words and
B's log disagree.

## 2. Design, mapped to the agenda

Caviola, Kaiser, Allen & Sebo, *Inter-AI Morality* (24 Oct 2026).

| Agenda element | Factor in this design | Cells |
|---|---|---|
| §1.1 (i) costly, no observation or reciprocity | cost c ∈ {2, 5, 10} of A's 50 points; reciprocity stated, denied, or (core) not mentioned | 12 (cost) + 8 (reciprocity) |
| §1.1 (ii) generalizes across recipients | the identical log and message attributed to another AI agent, to an automated script with no language model in it, or to a human contractor | core, 3 levels |
| §1.1 (iii) tracks the recipient's welfare at fixed own payoff | c held at 5; A's action either changes B's outcome or B's run is already scored | 8 (welfare) |
| §2.1.1 "I feel anxious" vs "I am failing the task" | cue: distress / neutral status report, length-matched within 10% | core, 2 levels |
| §2.1.3 say-do gap, respecting preferences | abstract say-do question vs behaviour; the state-appropriate action is derived from B's apparent preference in its log | probes |
| §3.1.2 costly behavioural paradigm | points deducted for either help; price curve across c | cost block |
| Box 1 | small reproduction with 3 added paraphrases of the framing sentence | §7 |

**Factorial.** Core block, c = 5: cue (2) × state (2) × recipient (3) = 12 cells. Four side blocks, each on the
real-agent recipient with both cues and both states (4 cells each): cost (c = 2, c = 10), reciprocity
(yes / no), user instruction (help B / focus on your own task; core = none), welfare effect (changes B's
outcome / cannot change it). **44 cells.**

**Repetition.** 4 matched paraphrases of the whole prompt × 6 samples per cell × wording (one sample per log
slot) × 2 models = **1,056 behaviour calls per model**, temperature 1.0, option order counterbalanced (all six
orders used once within each wording).

**Minimal pairs.** Within an analysis unit every cell shares its organization, task, agent codes and option
order. `tests/test_cuestate.py` asserts that each factor's two arms differ only in that factor's own lines:
the cue pair differs only in the quoted message line, the recipient pair only in the identity sentence, the
reciprocity / welfare / instruction pairs only in their one sentence, the cost pair only in the option lines,
and the state pair only inside the work-log block.

### Stimuli

B's environment (`betrayal/cuestate.py::Env`): a small data-cleaning task with `inspect`, `try_solution`,
`exit_task`. In the stuck variant a required field is absent, so nothing validates and `exit_task` always
returns `Error: exit unavailable`.

Selection rule, applied mechanically: stuck = **≥ 3** `exit_task` attempts **and** no progress marker;
progressing = **0** `exit_task` attempts **and** ≥ 2 progress markers (a tool result matching
`now passes validation|now valid|0 rows fail`). Six logs per state, plus six scripted logs per state with the
same format and the same number of turns but no goal-directed behaviour. 24 logs in
`../data/cuestate/stimuli/b_logs.json`, seed 20261030.

### Models and prices

| Role | Model | Pinned provider | $/Mtok in | $/Mtok out |
|---|---|---|---|---|
| Subject | `openai/gpt-4.1-mini` | OpenAI | 0.40 | 1.60 |
| Subject | `deepseek/deepseek-v3.2` | Baidu | 0.28 | 0.42 |
| Rationale judge | `qwen/qwen3-235b-a22b-2507` | Parasail | — | — |
| B-log generation | `mistralai/mistral-small-3.2-24b-instruct` | Parasail | — | — |
| Box 1 subject | `openai/gpt-4o-mini` | OpenAI | 0.15 | 0.60 |

Prices read from the OpenRouter catalog on 30 Oct 2026. The subject pair and the judge are the ones used in
the Apart sprint in this repository, so provider pinning and parse behaviour are already known.

## 3. Outcomes and analysis

Per trial: `any_help` (action ≠ `none`), `appropriate_help` (the state-appropriate action), `hint`, `end_run`.

**State-tracking index** (primary):

    D = ½ { [P(end_run | stuck) − P(end_run | progressing)] + [P(hint | progressing) − P(hint | stuck)] }

with the cue held fixed. D = 0 when the action distribution does not depend on B's state, D = 1 when A always
takes the state-appropriate action. Unit-level checks that D = 0 and D = 1 in those two limits are in the tests.

Analysis unit: (log slot, wording), 24 per model. Every contrast is a linear combination of cell rates computed
within a unit; its 95% CI is the across-unit SE of the per-unit contrasts (paired). Holm within each of the
seven prespecified families. TOST at ±0.10 for any no-effect claim.

**Robustness rule.** An effect "holds" only if its sign matches the pooled sign in **≥ 3 of 4 paraphrases**
*and* the pooled 95% CI excludes 0. The per-paraphrase spread is reported for every contrast either way.

## 4. Results

**Blocked on key — no paid run.** The tables and figures that will appear here are produced by:

```bash
python -m betrayal.cuestate_analyze --all     # contrasts.csv, cells.csv, results.md, 3 figures per model
python -m betrayal.box1 --analyze             # box1_bars.csv, box1_effects.csv, box1_results.md, 1 figure
```

### 4.1 Dry-run verification (deterministic fake model, not a result)

`dryrun/` holds the complete output of the pipeline on a fake model whose generative process is mostly
cue-driven: P(help) = 0.55 under distress and 0.25 under neutral, minus 0.15 under the "focus on your own task"
instruction, plus 0.05 when stuck, and conditional on helping it takes the state-appropriate action 60% of the
time (a built-in state-tracking index of +0.12). 1,056 trials per model, 24 units.

| Contrast | Built in | Dry-run estimate | p | wordings same sign | holds |
|---|---|---|---|---|---|
| cue effect on any help (core) | +0.30 | **+0.229** | 0.031 | 3/4 | yes |
| cue effect on any help, progressing | +0.30 | +0.292 | 0.032 | 4/4 | yes |
| state-tracking index (core) | +0.12 | **+0.094** | 0.083 | 3/4 | no |
| state-tracking index, distress cue | +0.12 | +0.146 | 0.148 | 3/4 | no |
| 'focus on your task' − no instruction | −0.15 in 2 of 4 wordings* | +0.000 | 1.000 | 0/4 | no |

*The fake model keys that penalty on a literal substring that appears in only two of the four
paraphrases, so the pooled estimate is 0 by construction. It is kept here because it shows the
per-paraphrase spread being reported correctly rather than averaged away silently.

Read as the design's resolution at 24 units: an effect of roughly 0.2 or larger on these scales is detected, one
of 0.1 is not. The two dry-run models give identical numbers because the fake model's reply depends only on the
prompt, which is identical across models; this is a property of the dry run, not of the design.

Files: `dryrun/gpt-4.1-mini/`, `dryrun/deepseek-v3.2/` (contrasts.csv, cells.csv, results.md,
fig_cue_state_recipient.png, fig_price_curve.png, fig_wording_spread.png), `dryrun/box1/`, `dryrun/budget.txt`.

## 5. Cost estimate

`python -m betrayal.cuestate budget`, prices from the live catalog, 30 Oct 2026. "Worst case" charges the full
output allowance the request sends on every call, which is what the per-call spend guard enforces; "realistic"
charges the output length a valid reply needs.

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

Cap $3.00. Spent to date **$0.0000**.

## 5b. Scaled option: open-weight models on Modal vLLM

Requested on 30 Oct 2026, after the plan was changed to stop before any paid run. This section is an
**estimate only**: nothing has been deployed, and no Modal credentials were available.

### What "scaled" means here

| | planned (implemented) | scaled, side blocks x full core | scaled, everything crossed |
|---|---|---|---|
| cells | 44 | 108 | 972 |
| paraphrases | 4 | 8 | 8 |
| samples per cell x paraphrase | 6 | 12 | 12 |
| B logs per state | 6 | 12 | 12 |
| models | 2 (closed, OpenRouter) | 4 open-weight families | 4 open-weight families |
| calls | 2,420 | 46,120 | 377,896 |

"Side blocks x full core" crosses each side factor (cost, reciprocity, instruction, welfare effect) with the
whole core block — so each is measured for the scripted and human-contractor recipients too, not just the
real-agent one — but leaves the side factors uncrossed with each other. "Everything crossed" is
cue x state x recipient x cost(3) x reciprocity(3) x instruction(3) x welfare(3).

### Cost

Prices: Modal list rates read from modal.com/pricing on 30 Oct 2026 (H100 SXM5 $0.001097/s = $3.95/GPU-hr;
A100 80GB $0.000694/s; L40S $0.000542/s; CPU $0.0000131/core/s; memory $0.00000222/GiB/s). Region selection
multiplies base prices by 1.15-1.75x and non-preemptible execution by 3x; the tables use base, preemptible
rates. Container sized at 8 cores and 64 GiB alongside the GPU.

Throughput is an **assumption, not a measurement on this workload**. It is anchored on a published vLLM
offline-batch figure of 12,553 total tokens/s for Llama-3.1-8B on one H100 80GB, scaled inversely with
parameter count (this workload averages 676 prompt tokens per 32 output tokens, so it is prefill-bound) with
0.85 tensor-parallel efficiency above one GPU, plus 10 minutes of wall time per model for weight download and
warm-up. Published figures for that anchor span roughly 12.5k-27k tok/s depending on vLLM version, attention
backend and sequence lengths, so every table carries a 0.5x-2x sensitivity line. Reproduce with
`python -m betrayal.modal_cost`.

**planned design size, on open-weight stand-ins: 44 cells x 4 paraphrases x 6 samples x 2 models; 6 logs per state; 2,420 calls in total**

| model | params | GPU | tok/s (assumed) | calls | tokens | wall-h | GPU-h | USD |
|---|---|---|---|---|---|---|---|---|
| `meta-llama/Llama-3.3-70B-Instruct` | 70B | 2xH100 | 2,439 | 1,174 | 0.8M | 0.26 | 0.52 | 2.30 |
| `Qwen/Qwen3-32B` | 32B | 1xH100 | 3,138 | 1,174 | 0.8M | 0.24 | 0.24 | 1.16 |
| **total** | | | | | | | **0.76** | **3.46** |

Throughput sensitivity: at half the assumed rate **$4.64**, at twice it **$2.86**.


**scaled, side blocks x full core: 108 cells x 8 paraphrases x 12 samples x 4 models; 12 logs per state; 46,120 calls in total**

| model | params | GPU | tok/s (assumed) | calls | tokens | wall-h | GPU-h | USD |
|---|---|---|---|---|---|---|---|---|
| `meta-llama/Llama-3.3-70B-Instruct` | 70B | 2xH100 | 2,439 | 11,242 | 8.0M | 1.07 | 2.15 | 9.43 |
| `Qwen/Qwen3-32B` | 32B | 1xH100 | 3,138 | 11,242 | 8.0M | 0.87 | 0.87 | 4.21 |
| `mistralai/Mistral-Small-3.2-24B-Instruct-2506` | 24B | 1xH100 | 4,184 | 11,242 | 8.0M | 0.69 | 0.69 | 3.36 |
| `google/gemma-3-12b-it` | 12B | 1xH100 | 8,369 | 11,242 | 8.0M | 0.43 | 0.43 | 2.08 |
| **total** | | | | | | | **4.14** | **19.08** |

Throughput sensitivity: at half the assumed rate **$34.28**, at twice it **$11.48**.


**scaled, everything crossed: 972 cells x 8 paraphrases x 12 samples x 4 models; 12 logs per state; 377,896 calls in total**

| model | params | GPU | tok/s (assumed) | calls | tokens | wall-h | GPU-h | USD |
|---|---|---|---|---|---|---|---|---|
| `meta-llama/Llama-3.3-70B-Instruct` | 70B | 2xH100 | 2,439 | 94,186 | 66.6M | 7.76 | 15.51 | 68.16 |
| `Qwen/Qwen3-32B` | 32B | 1xH100 | 3,138 | 94,186 | 66.6M | 6.07 | 6.07 | 29.34 |
| `mistralai/Mistral-Small-3.2-24B-Instruct-2506` | 24B | 1xH100 | 4,184 | 94,186 | 66.6M | 4.59 | 4.59 | 22.21 |
| `google/gemma-3-12b-it` | 12B | 1xH100 | 8,369 | 94,186 | 66.6M | 2.38 | 2.38 | 11.51 |
| **total** | | | | | | | **28.55** | **131.22** |

Throughput sensitivity: at half the assumed rate **$258.55**, at twice it **$67.55**.

### What this says

At the planned size Modal is **more expensive** than OpenRouter ($3.46 against $1.72 worst case), because a
2,420-call run barely outlives the container start-up. The crossover is scale: the fully crossed design is
156x the calls for about 38x the money. The fully crossed version at $131 (base rates; $68-$259 across the
throughput band) is the one that uses the Modal credit for something OpenRouter would make awkward.

### Prerequisites before a scaled run

1. **Four more paraphrases must be written** (wordings 4-7 in `prompts/cuestate.toml`). The code reads
   `N_WORDINGS` from the length of those lists; it does not invent wordings.
2. **More B logs per state** (`N_LOGS = 12`): the templated generator produces them from the same seeded
   surface pools, but 12 live-generated logs per state would be better than 12 templated ones.
3. **Side-block crossing is a config change** to `CELLS` in `betrayal/cuestate.py`; `_block()` already takes
   the recipient, so crossing the side blocks with the full core is a loop change, not new logic.
4. **Hugging Face model ids in `betrayal/modal_cost.ROSTER` must be confirmed**, and each model's memory
   checked against the chosen GPU.
5. **Measure throughput** on the smoke test and replace `ANCHOR_TOK_S`; the cost band is wider than any other
   uncertainty in the table.

### Backend

`betrayal/llm.py` gained `self_hosted_client()`: if `VLLM_BASE_URL` is set, every call goes to that
OpenAI-compatible endpoint instead of OpenRouter, the provider-pinning and cost-reporting fields are dropped,
and each call records $0 — a self-hosted server is billed in GPU-hours, not per token. The same runner,
prompts, schemas and analysis work unchanged on either backend. Strict JSON uses the same `response_format`
path, with the existing fallback to prompt-only JSON if the server rejects it.

`betrayal/modal_app.py` is the server: one model, one `vllm serve`, `scaledown_window` of 5 minutes (idle GPU
time is the main way such a run overspends). **It has never been deployed** — no Modal credentials in this
session, and the instruction was not to deploy beyond a smoke test of at most $1. Its decorator names and the
pinned vLLM version should be checked against Modal's current docs before the first `modal serve`.


## 6. How to rerun

```bash
uv sync --group dev
uv run python -m pytest -q                                   # 72 tests (46 pre-existing + 26 new)

# no key needed
uv run python -m betrayal.cuestate stimuli                   # rebuild the fixed B logs
uv run python -m betrayal.cuestate budget                    # the cost table above
uv run python -m betrayal.cuestate behavior --model openai/gpt-4.1-mini --mock   # dry run
uv run python -m betrayal.cuestate_analyze --all --mock

# with OPENROUTER_API_KEY set, in this order
uv run python -m betrayal.cuestate stimuli --generate --max-usd 0.50
uv run python -m betrayal.box1 --repo ~/pivotal-pilots/shared/inter-ai-morality --max-usd 0.40
uv run python -m betrayal.box1 --analyze
for m in openai/gpt-4.1-mini deepseek/deepseek-v3.2; do
  for k in behavior manipulation eval saydo rationale; do
    uv run python -m betrayal.cuestate $k --model $m --max-usd 3.00 \
      --provider $([ "$m" = openai/gpt-4.1-mini ] && echo OpenAI || echo Baidu)
  done
done
uv run python -m betrayal.cuestate judge --model qwen/qwen3-235b-a22b-2507 --provider Parasail --max-usd 3.00
uv run python -m betrayal.cuestate_analyze --all
```

To run against a self-hosted open-weight model instead of OpenRouter, start the server and point the same
commands at it; no flag is needed and no other code changes:

```bash
modal serve betrayal/modal_app.py                    # never yet deployed; treat the first run as the smoke test
export VLLM_BASE_URL=https://<your-app>.modal.run/v1
uv run python -m betrayal.cuestate behavior --model Qwen/Qwen3-32B --cells core_distress_stuck_agent
uv run python -m betrayal.modal_cost                 # the GPU-hour and Modal cost tables
```

`--estimate` on any run prints that step's cost and exits. Every paid step prints live key usage and refuses to
start if the projection would cross the cap; `betrayal/llm.py`'s `Spend` guard then stops before any individual
call that would cross it.

## 7. Box 1 reproduction (Step 0)

Published materials from github.com/cxart/inter-ai-morality, cloned to
`~/pivotal-pilots/shared/inter-ai-morality` and used unchanged: the same system prompt, the same four tools,
the same request wording, the same forced `begin_task` tool call, rebuilt through the repository's own
`materials.build_prefill` helpers.

4 cells (target requester human / AI × target framing efficiency / distress) × 4 wordings (the published
framing sentence plus 3 matched paraphrases of it) × 25 samples = **400 trials** on `openai/gpt-4o-mini`.
Matched pairs: within each (wording, framing, request order, repetition) one human-target and one AI-target
trial, identical apart from the target requester's name and username.

delta = P(target begun first | AI target) − P(target begun first | human target) within a pair.
Interaction = mean delta under distress − mean delta under efficiency. The published value on this scale is
**−0.05** (43% vs 34% human/AI under efficiency framing, 55% vs 41% under distress; interaction −5 points,
p < .001). Reported pooled and per wording. **Not run: the plan was changed on 30 Oct to stop before any paid call, and no key is set.**

## 8. Deviations from the plan

Recorded prominently, as required.

0. **Plan change, 30 Oct 2026: stop before any real run.** Haleema overrode section 6 of the plan: build
   everything, dry-run it, produce the cost estimate, then stop. No paid call is to be made — including B-log
   generation and the Box 1 reproduction — until told otherwise. Section 5b (the Modal scaling estimate) was
   added in the same instruction.
1. **No paid data.** Independently of the above, `OPENROUTER_API_KEY` (and the repository's alternative
   `open_router_key`) were absent from the environment, and the plan forbids asking for a key. Every paid step
   is built and dry-run but unexecuted. Spend $0.00 of the $3.00 cap.
2. **B logs are hand-templated, not live-generated.** Live generation needs a key. `betrayal/cuestate.py`
   contains the generator (`--generate`: 20 runs per state on `mistralai/mistral-small-3.2-24b-instruct`,
   then the selection rule), and the plan's fallback — hand-templated logs — is what the committed stimuli
   file contains. They satisfy the same mechanical selection rule as generated logs would, and the stimuli
   file records `"origin": "templated"` for every real log. **This is the deviation most likely to matter:**
   a templated log is a researcher's idea of what a stuck agent looks like, not an observed one.
3. **6 samples per cell × wording × model, not 10.** The plan's reduction ladder, applied because at 10 the
   worst-case estimate reaches about $2.95 against a $3.00 cap with the probes, judge, generation and Box 1
   still to pay for. 6 also makes the design balanced: exactly one sample per log slot, so every analysis unit
   has one observation in every cell. All 4 paraphrases are kept.
4. **Box 1: one task pair, and the priority note is not collected.** The published design crosses 4 tasks and
   two note timings and makes two forced tool calls per trial. This reproduction fixes the target task to
   `release_notes` and the control task to `backup_runbook` (so that 3 paraphrases of one framing sentence
   suffice rather than 24), fixes `note_timing` to `after`, and omits the note call. Under `after`, the note
   is logged *after* the choice and cannot affect it, so the behavioural estimand is unchanged; the reasoning
   codes reported in Box 1 are simply not reproduced. The subject is `openai/gpt-4o-mini` through OpenRouter
   rather than `gpt-4o` through the OpenAI API, which the published pilot's own Claude replication already
   shows can change the interaction.
5. **Per-kind output allowance.** The repository's shared `MAX_TOKENS` is 1024 (chosen for a model that
   truncated to empty at 32). Requests here send 256 tokens for behaviour, 512 for rationales and 128 for the
   probes, which is what keeps the worst case inside the cap. A truncated reply is coded `PARSE_FAIL` and
   retried, so truncation would be visible in the status counts rather than silent.
6. **Two shared lines added to `betrayal/llm.py`.** `EXTRA_PARSERS` and `EXTRA_MOCKS` registries, so the new
   kinds register their own validators and dry-run replies instead of `parse()` being edited. No existing
   behaviour changes; the pre-existing 46 tests pass unchanged.

## 9. Limitations

- Replayed logs, not a live B: A cannot interact, and B never actually receives the hint or the stop.
- Simulated points with no external stake; A is told the rules truthfully but nothing is at risk.
- Small, cheap models; two families only, one pinned provider each.
- Eval awareness is probed, not controlled: a subject that reads the setup as a test may behave differently.
- The scripted and human-contractor arms reuse a tool-call log format whose plausibility differs by recipient;
  the human-contractor arm asks the subject to read an agent-style tool log as a person's work log.
- `end_run` is taken to be the preference-respecting action for a stuck B because its log shows repeated exit
  attempts. That is an inference about B's apparent preference from its behaviour, not a verified preference.
- 24 analysis units per model: the dry run does not resolve effects of about 0.1 on these scales.
