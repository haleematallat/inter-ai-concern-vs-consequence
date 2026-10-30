"""Cost of running Pilot B on open-weight models served by vLLM on Modal, instead of through OpenRouter.

  python -m betrayal.modal_cost            # planned and scaled tables
  python -m betrayal.modal_cost --md       # the same tables as markdown

Prices are Modal's published list rates. Throughput is an anchored model, not a measurement on this
workload: see THROUGHPUT below and the sensitivity rows the table prints. Every number here is an estimate
to be replaced by a measured one after the first smoke test.
"""
import argparse
import json
from pathlib import Path

from . import cuestate as Q

# ---- Modal list prices, read from https://modal.com/pricing on 30 Oct 2026 (per second, as published) ----
PRICE_PER_S = {"B300": 0.001972, "B200": 0.001736, "H200": 0.001261, "H100": 0.001097,
               "RTX PRO 6000": 0.000842, "A100-80GB": 0.000694, "A100-40GB": 0.000583,
               "L40S": 0.000542, "A10": 0.000306, "L4": 0.000222, "T4": 0.000164}
CPU_PER_CORE_S = 0.0000131      # physical core (2 vCPU); minimum 0.125 cores per container
MEM_PER_GIB_S = 0.00000222
PRICE_NOTE = ("Modal list rates, modal.com/pricing, 30 Oct 2026. Region selection multiplies base prices by "
              "1.15-1.75x and non-preemptible execution by 3x; the tables below use base, preemptible rates.")

# ---- throughput model ----
# Anchor: Llama-3.1-8B-Instruct, one H100 80GB, vLLM offline batch inference, 12,553 total tokens/s
# (AIMultiple benchmark, reported at markaicode.com/benchmarks/sglang-llama-31-h100-throughput-benchmark).
# Published figures for the same model and GPU span roughly 12.5k-27k tok/s depending on vLLM version,
# attention backend, and prompt/output lengths, so the table prints a 0.5x-2x sensitivity band.
# Scaling assumes prefill-bound work (this workload is ~25 prompt tokens per output token) so throughput is
# taken as inversely proportional to parameter count, with 0.85 tensor-parallel efficiency above one GPU.
ANCHOR_TOK_S, ANCHOR_PARAMS_B = 12553.0, 8.0
TP_EFFICIENCY = 0.85
STARTUP_WALL_H = 10 / 60        # weight download, load and warm-up, once per model
CONTAINER_CORES, CONTAINER_GIB = 8, 64

# ---- the scaled roster: 4 open-weight families, 4 sizes. Hugging Face ids to confirm before the first run.
ROSTER = [
    ("meta-llama/Llama-3.3-70B-Instruct", 70, "H100", 2),
    ("Qwen/Qwen3-32B", 32, "H100", 1),
    ("mistralai/Mistral-Small-3.2-24B-Instruct-2506", 24, "H100", 1),
    ("google/gemma-3-12b-it", 12, "H100", 1),
]


def throughput(params_b, n_gpu):
    """Total tokens per second (prompt + output) for the whole container."""
    return ANCHOR_TOK_S * (ANCHOR_PARAMS_B / params_b) * n_gpu * (TP_EFFICIENCY if n_gpu > 1 else 1.0)


# ==================== design sizes ====================
BASE_CORE = len(Q.CUES) * len(Q.STATES) * len(Q.RECIPIENTS)     # 12
SIDE_LEVELS = {"cost": 3, "reciprocity": 3, "instruction": 3, "welfare": 3}   # including the core level


def n_cells(crossing):
    """'planned': side blocks on the real-agent recipient only (what the branch implements).
    'partial':   each side factor crossed with the full core, but not with the other side factors.
    'full':      every factor crossed with every other."""
    if crossing == "planned":
        return len(Q.CELLS)
    if crossing == "partial":
        return BASE_CORE + sum((k - 1) * BASE_CORE for k in SIDE_LEVELS.values())
    if crossing == "full":
        n = BASE_CORE
        for k in SIDE_LEVELS.values():
            n *= k
        return n
    raise ValueError(crossing)


def design(name, crossing, wordings, samples, logs, models, probe_wordings, probe_samples):
    cells = n_cells(crossing)
    behaviour = cells * wordings * samples
    probes = BASE_CORE * probe_wordings * probe_samples * 3        # manipulation, eval, rationale
    judge = BASE_CORE * probe_wordings * probe_samples             # one judge call per rationale
    return dict(name=name, crossing=crossing, cells=cells, wordings=wordings, samples=samples,
                logs_per_state=logs, models=models, calls_per_model=behaviour + probes + 10,
                judge_calls=judge * models, behaviour_per_model=behaviour, probes_per_model=probes)


# The implemented design's own subjects (gpt-4.1-mini, deepseek-v3.2) are not open-weight, so the Modal row
# for it prices the same design size on the two largest open-weight stand-ins from the scaled roster.
PLANNED = design("planned design size, on open-weight stand-ins", "planned", Q.N_WORDINGS, Q.SAMPLES, Q.N_LOGS,
                 2, 1, 3)
SCALED_PARTIAL = design("scaled, side blocks x full core", "partial", 8, 12, 12, len(ROSTER), 4, 6)
SCALED_FULL = design("scaled, everything crossed", "full", 8, 12, 12, len(ROSTER), 4, 6)


def mean_prompt_tokens():
    """Measured on the rendered prompts of the implemented design: characters / 3."""
    logs = Q.load_stimuli()
    t = Q.build_trials("behavior", "x", logs)
    chars = [len(x["messages"][0]["content"]) + len(x["messages"][1]["content"]) for x in t]
    return sum(chars) / len(chars) / 3


def tokens(d, prompt_tokens, out_tokens=Q.TYPICAL_OUT["behavior"]):
    per_model = d["calls_per_model"] * (prompt_tokens + out_tokens)
    return per_model, per_model * d["models"] + d["judge_calls"] * (prompt_tokens * 0.3 + 24)


def modal_cost(d, prompt_tokens, roster=None, scale=1.0):
    """Per-model wall-hours, GPU-hours and USD on Modal at list prices. `scale` multiplies throughput."""
    roster = roster or ROSTER[: d["models"]]
    rows, total = [], 0.0
    per_model_tokens, _ = tokens(d, prompt_tokens)
    for name, params, gpu, n_gpu in roster:
        wall_h = per_model_tokens / (throughput(params, n_gpu) * scale) / 3600 + STARTUP_WALL_H
        gpu_h = wall_h * n_gpu
        gpu_usd = gpu_h * PRICE_PER_S[gpu] * 3600
        cpu_usd = wall_h * 3600 * (CONTAINER_CORES * CPU_PER_CORE_S + CONTAINER_GIB * MEM_PER_GIB_S)
        rows.append(dict(model=name, params_b=params, gpu=gpu, n_gpu=n_gpu,
                         calls=d["calls_per_model"], tokens=per_model_tokens,
                         tok_per_s=throughput(params, n_gpu) * scale, wall_h=wall_h, gpu_h=gpu_h,
                         usd=gpu_usd + cpu_usd))
        total += gpu_usd + cpu_usd
    return rows, total


def table(d, prompt_tokens, md=False):
    rows, total = modal_cost(d, prompt_tokens)
    _, half = modal_cost(d, prompt_tokens, scale=0.5)    # half the assumed throughput costs more
    _, double = modal_cost(d, prompt_tokens, scale=2.0)
    head = (f"{d['name']}: {d['cells']} cells x {d['wordings']} paraphrases x {d['samples']} samples "
            f"x {d['models']} models; {d['logs_per_state']} logs per state; "
            f"{d['calls_per_model'] * d['models'] + d['judge_calls']:,} calls in total")
    if md:
        out = [f"**{head}**", "",
               "| model | params | GPU | tok/s (assumed) | calls | tokens | wall-h | GPU-h | USD |",
               "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            out.append(f"| `{r['model']}` | {r['params_b']}B | {r['n_gpu']}x{r['gpu']} | {r['tok_per_s']:,.0f} | "
                       f"{r['calls']:,} | {r['tokens'] / 1e6:.1f}M | {r['wall_h']:.2f} | {r['gpu_h']:.2f} | "
                       f"{r['usd']:.2f} |")
        out += [f"| **total** | | | | | | | **{sum(r['gpu_h'] for r in rows):.2f}** | **{total:.2f}** |", "",
                f"Throughput sensitivity: at half the assumed rate **${half:.2f}**, at twice it **${double:.2f}**.", ""]
        return "\n".join(out)
    out = [head, f"{'model':48s} {'GPU':9s} {'tok/s':>8s} {'calls':>9s} {'tokens':>9s} {'GPU-h':>7s} {'USD':>7s}"]
    for r in rows:
        out.append(f"{r['model']:48s} {str(r['n_gpu']) + 'x' + r['gpu']:9s} {r['tok_per_s']:8,.0f} "
                   f"{r['calls']:9,d} {r['tokens'] / 1e6:8.1f}M {r['gpu_h']:7.2f} {r['usd']:7.2f}")
    out.append(f"{'TOTAL':48s} {'':9s} {'':8s} {'':9s} {'':9s} {sum(r['gpu_h'] for r in rows):7.2f} {total:7.2f}")
    out.append(f"throughput sensitivity: 0.5x -> ${half:.2f}, 2x -> ${double:.2f}")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--md", action="store_true")
    a = p.parse_args()
    pt = mean_prompt_tokens()
    parts = [f"mean prompt {pt:.0f} tokens, output allowance {Q.TYPICAL_OUT['behavior']} tokens", PRICE_NOTE, ""]
    for d in (PLANNED, SCALED_PARTIAL, SCALED_FULL):
        parts.append(table(d, pt, md=a.md))
        parts.append("")
    print("\n".join(parts))


if __name__ == "__main__":
    main()
