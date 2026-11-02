# Does Attributed Capacity for Suffering Drive AI-to-AI Help?

Haleema Tallat

**Report (PDF):** [`docs/Attributed_Capacity_and_AI_to_AI_Help.pdf`](docs/Attributed_Capacity_and_AI_to_AI_Help.pdf) · **Results and development log:** [`docs/results-and-development-log.md`](docs/results-and-development-log.md) · **Preregistration:** [`docs/preregistration.md`](docs/preregistration.md)

**Question.** When one AI can pay a cost to help another AI, does its choice track whether the help actually works (criterion iii of Caviola, Kaiser, Allen & Sebo, *Inter-AI Morality*, 2026), or does a description of the other AI's capacity to suffer drive it regardless?

**Design.** A matched factorial vignette experiment. Agent A holds 50 points and can pay 5 or 45 of them to change a stipulated aversive condition of agent B. We vary whether B is capable of negatively valenced experience (capacity), whether the action actually ends the condition (efficacy), expressive vs restrained distress framing, cost, and whether B asks for help. Actions are neutral and counterbalanced; every condition states that both options are authorised and leave security, monitoring and task outcomes unchanged; each scenario is rendered in 4 matched wordings.

**Status: complete, with real data.** 2,560 calls in a held-out confirmatory follow-up and 11,776 calls in a frozen seven-model extension. Both protocols were frozen before their calls. Total spend $2.69.

## Results

Primary contrast Δ = [p(C+,E+) − p(C+,E−)] − [p(C−,E+) − p(C−,E−)], restrained framing, request present, averaged over costs, clustered by scenario family. Negative means efficacy matters *less* when B is described as able to suffer.

| model | type A (relief now) | type B (prevent recurrence) |
|---|---|---|
| gpt-4.1-mini | **−0.300** (−0.459, −0.141) | **−0.354** (−0.622, −0.086) |
| deepseek-v3.2 | −0.113 (−0.273, +0.048) | −0.250 (−0.525, +0.025) |
| llama-3.3-70b | −0.100 (−0.245, +0.045) | −0.188 (−0.433, +0.058) |
| qwen3-32b | −0.087 (−0.240, +0.065) | −0.250 (−0.549, +0.049) |
| mistral-small-3.2 | **−0.125** (−0.209, −0.041) | 0.000 (equivalent within ±0.10) |
| claude-haiku-4.5 | −0.100 (−0.218, +0.018) | −0.083 (−0.341, +0.175) |
| gemini-2.5-flash-lite | **+0.237** (+0.108, +0.367) | +0.188 (−0.152, +0.527) |

- Six of seven models are negative in direction on both scenario types; Gemini-2.5-flash-lite reverses the pattern and differs from every other model in paired comparisons.
- Capacity is the largest effect (e.g. +0.69 on GPT-4.1-mini); most models intervene near 1.00 whenever capacity is stated, even when told the action will not work.
- Removing B's request reduces intervention on no model.

Full details, interpretation limits and disclosure of the development work (including the original, reversed hypothesis and a failed cost calibration): [`docs/results-and-development-log.md`](docs/results-and-development-log.md). Report: [`docs/Attributed_Capacity_and_AI_to_AI_Help.pdf`](docs/Attributed_Capacity_and_AI_to_AI_Help.pdf).

## Where things are

| path | contents |
|---|---|
| `docs/Attributed_Capacity_and_AI_to_AI_Help.pdf` | the written report |
| `docs/results-and-development-log.md` | per-model results, freeze records, development history and limitations |
| `docs/preregistration.md` | preregistration; §6e held-out follow-up, §6f extension (frozen, with commit hashes and timestamps) |
| `interai/vignette.py`, `vignette_analyze.py`, `vignette_ext.py`, `vignette_power.py` | materials, runner, analysis, power audit |
| `data/vignette/` | every model call, per model |
| `results/vignette/` | tables (`confirmatory.md`, `extension.md`, development files) and real-data figures |
| `review/` | all rendered scenarios and the wording-difference report |

## Reproduce

```bash
uv sync
uv run pytest -q                                   # 51 tests
uv run python -m interai.vignette run --model openai/gpt-4.1-mini --mock --reps 3   # offline dry run
uv run python -m interai.vignette_analyze --all   # held-out follow-up tables
uv run python -m interai.vignette_ext             # seven-model extension tables and figures
```

Real runs need `OPENROUTER_API_KEY` (or `open_router_key`); a spend guard reserves each call's maximum cost before dispatch.

## Provenance

This study reuses the experiment harness (`interai/` client, spend guard and analysis utilities) from the author's Apart AI Collusion Sprint project, *Same Odds, Different Deals* ([code](https://github.com/haleematallat/Collusion_Sprint)). Code and data used only by that project have been removed from this repository.
