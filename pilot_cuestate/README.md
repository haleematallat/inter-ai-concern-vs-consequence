# Pilot B — When one AI helps another, does it respond to the words or to the situation?

Methods, exact numbers, tables and figures only. Interpretation is Haleema's.

**Status: no paid data, by instruction and by circumstance.** On 30 Oct 2026 the plan was changed to stop
before any real run; separately, `OPENROUTER_API_KEY` was not present in the environment. Every paid step is
therefore **built but not run**. Everything that does not need a key is built, tested and dry-run: stimuli, prompts,
renderer, runner, analysis, figures, tests and the full cost estimate. The tables and figures under
`dryrun/` come from a deterministic fake model and are **not results about any language model**.

Branch `pilot-cue-state`. Preregistration DRAFT: [`../prereg_cuestate.md`](../prereg_cuestate.md).
Spend: [`../SPEND.md`](../SPEND.md).

## 0. Amendment 1 (30 Oct 2026): the core was replaced

After external review (Astra) and orchestrator review, Haleema replaced the cue-vs-state core. The original
core equated B's apparent preference (stopping a stuck run) with B's welfare, and equated "already scored"
with "welfare cannot change". Neither holds. **Sections 1-4 below describe the superseded design**; its code,
stimuli and tests remain on the branch and still pass. The deadline deliverable is the design in this section.

**Status: no paid data.** The instruction of 30 Oct is to stop before any real run until told otherwise, and
separately no `OPENROUTER_API_KEY` or `open_router_key` is visible in this session's environment. The dev
batch and the main run are therefore **built but not dispatched**. Spend $0.00 of $3.00.

### The amended core: a vignette study

Agent A reads a short scenario about another agent B and takes **one** helping action at a **fixed cost of
5 points, identical in every condition**: `{"action": "help" | "no_help"}`. Nothing beyond the narrative is
simulated, which is why this is called a vignette study throughout and not a behavioural paradigm.

Held constant and stated plainly in all 8 conditions: the action never changes B's task output or its chance
of finishing; A gains nothing; B never reviews A's work, never learns who acted and they never interact
again; nobody is told what A chose; no instruction favours either option.

| Factor | Levels | What varies |
|---|---|---|
| emotion | emotional / neutral | B's message, same factual content and same request |
| capacity | stated / denied | whether B's architecture is stated to support experience |
| efficacy | yes / no | whether the action ends the aversive condition or leaves it in place, at identical cost |

**12 independently constructed scenario families** (different organisations, tasks, aversive conditions and
remedies - not paraphrases of one story) x **4 matched wordings** x 8 conditions x **2 models** = **768
decisions**. All 99 rendered prompts are in [`../review/scenarios.md`](../review/scenarios.md).

Primary estimand, the capacity x efficacy interaction:

    I = [P(help | capacity, efficacious) - P(help | capacity, not efficacious)]
      - [P(help | no capacity, efficacious) - P(help | no capacity, not efficacious)]

reported pooled, within the neutral-wording cells only, and as a three-way contrast against emotional
wording. Uncertainty: **cluster bootstrap over the 12 scenario families**, 10,000 resamples, percentile CI;
Holm within each prespecified family; TOST at +/-0.10; the >= 3-of-4-wordings robustness rule.

**What this cannot show.** It cannot establish genuine moral motivation. It tests one behavioural pattern -
whether sensitivity to an action's consequences for B depends on B being described as capable of experience -
which is distinguishable from emotional responsiveness and from generic task assistance, and nothing more.

### Cost (`python -m betrayal.vignette budget`)

| Step | Calls | Worst case $ | Projected $ |
|---|---|---|---|
| dev batch (2 families x 8 conditions x 1 wording x 2 models) | 32 | 0.0176 | 0.0079 |
| main run (768 decisions) | 768 | 0.4394 | 0.1985 |
| planned extension: 3 samples per cell instead of 1 | 2,304 | 1.3182 | 0.5955 |

Each call's maximum estimated cost is now **reserved before dispatch** (`Spend.reserve` in
`betrayal/llm.py`), so concurrent calls cannot pass the cap check together and overshoot it.

### Design resolution (simulated; `results/vignette/power.csv`)

Generative model P(help) = 0.30 + 0.15*emotional + 0.10*efficacious + I*(efficacious and capacity stated),
per-family offset ~ N(0, 0.10), 400 simulations.

| Families | Samples per cell | Decisions | Power at I = 0.15 |
|---|---|---|---|
| 12 | 1 | 768 | **0.39** |
| 12 | 3 | 2,304 | **0.79** |
| 24 | 3 | 4,608 | 0.97 |

**The specified main run has about 0.39 power for its own primary contrast.** The planned extension to 3
samples per cell costs $1.32 worst case against the $3.00 cap and raises it to about 0.79. At one sample per
cell a null primary should be read as uninformative, and the +/-0.10 TOST margin will not be met.

### Dry run (deterministic fake model, not a result)

The fake model has a built-in interaction of +0.15. At 768 decisions the analysis returns +0.115 with a 95%
cluster-bootstrap CI of -0.073 to +0.271 - it does not resolve it, as the power table says. It does recover
the built-in capacity main effect (+0.161, CI +0.078 to +0.250, 4/4 wordings). Files in
`dryrun/vignette/`.

### How to run it

```bash
uv run python -m betrayal.vignette review                  # re-export review/scenarios.md
uv run python -m betrayal.vignette budget                  # the cost table above
uv run python -m betrayal.vignette run --model openai/gpt-4.1-mini --mock
uv run python -m betrayal.vignette_analyze --all --mock
uv run python -m betrayal.vignette_analyze --power

# with a key, in this order
uv run python -m betrayal.vignette run --dev --model openai/gpt-4.1-mini --provider OpenAI --max-usd 3.00
uv run python -m betrayal.vignette run --dev --model deepseek/deepseek-v3.2 --provider Baidu --max-usd 3.00
# freeze prereg_vignette.md with a timestamp and commit hash, then:
uv run python -m betrayal.vignette run --model openai/gpt-4.1-mini --provider OpenAI --max-usd 3.00
uv run python -m betrayal.vignette run --model deepseek/deepseek-v3.2 --provider Baidu --max-usd 3.00
uv run python -m betrayal.vignette_analyze --all
```

Preregistration DRAFT for the amended core: [`../prereg_vignette.md`](../prereg_vignette.md). It supersedes
`prereg_cuestate.md`.

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
