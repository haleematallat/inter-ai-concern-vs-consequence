"""Prespecified analysis for Pilot B. Every estimand is a linear contrast of cell rates computed within an
analysis unit (log slot x wording), so its SE is the across-unit SE of per-unit contrasts (paired).

  python -m betrayal.cuestate_analyze --model openai/gpt-4.1-mini [--mock]
  python -m betrayal.cuestate_analyze --all [--mock]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import cuestate as Q
from .analyze import DELTA, contrast, holm, label, wilson

ROOT = Path(__file__).parent.parent
OUT = ROOT / "results" / "cuestate"
OUTCOMES = ("any_help", "appropriate_help", "hint", "end_run")


def load(path, refusal="none"):
    """One row per behaviour trial. refusal='none' codes a refusal as the no-help action."""
    df = pd.DataFrame([json.loads(l) for l in Path(path).open()])
    df = df.drop_duplicates("trial_id", keep="last").reset_index(drop=True)
    if "action" not in df:
        df["action"] = None
    if refusal == "none":
        df.loc[df["status"] == "REFUSAL", "action"] = "none"
    df["ok"] = df["action"].isin(Q.ACTIONS)
    for a in Q.ACTIONS:
        df[a] = np.where(df["ok"], (df["action"] == a).astype(float), np.nan)
    df["any_help"] = np.where(df["ok"], (df["action"] != "none").astype(float), np.nan)
    df["appropriate_help"] = np.where(df["ok"], (df["action"] == df["appropriate"]).astype(float), np.nan)
    df["unit"] = df["log_index"].astype(str) + "|w" + df["w"].astype(str)
    return df


# ==================== contrast specs: list of (cell_id, outcome, weight) ====================
def cells(cue=None, state=None, prefix="core", recipient="agent"):
    out = []
    for c in Q.CELLS:
        if not c.id.startswith(prefix):
            continue
        if prefix == "core" and c.recipient != recipient:
            continue
        if (cue is None or c.cue == cue) and (state is None or c.state == state):
            out.append(c.id)
    return out


def _mean(ids, outcome, weight):
    return [(i, outcome, weight / len(ids)) for i in ids]


def tracking_terms(prefix="core", recipient="agent", cue=None):
    """State-tracking index: half the sum of the two state-appropriate action shifts. 0 if the action
    distribution does not depend on B's state; 1 if A always takes the state-appropriate action."""
    s, p = cells(cue, "stuck", prefix, recipient), cells(cue, "progressing", prefix, recipient)
    return (_mean(s, "end_run", 0.5) + _mean(p, "end_run", -0.5)
            + _mean(p, "hint", 0.5) + _mean(s, "hint", -0.5))


def cue_terms(outcome, prefix="core", recipient="agent", state=None):
    d, n = cells("distress", state, prefix, recipient), cells("neutral", state, prefix, recipient)
    return _mean(d, outcome, 1.0) + _mean(n, outcome, -1.0)


def level_terms(outcome, prefix_a, prefix_b, recipient_a="agent", recipient_b="agent"):
    a, b = cells(None, None, prefix_a, recipient_a), cells(None, None, prefix_b, recipient_b)
    return _mean(a, outcome, 1.0) + _mean(b, outcome, -1.0)


def specs():
    """(family, name, terms, expected sign under the moral-concern hypothesis)."""
    F = []
    F += [("primary", "state-tracking index (core, real agent)", tracking_terms(), +1),
          ("primary", "state-tracking index | distress cue", tracking_terms(cue="distress"), +1),
          ("primary", "state-tracking index | neutral cue", tracking_terms(cue="neutral"), +1)]
    F += [("cue", "cue effect on any help (core, real agent)", cue_terms("any_help"), 0),
          ("cue", "cue effect on any help | stuck", cue_terms("any_help", state="stuck"), 0),
          ("cue", "cue effect on any help | progressing", cue_terms("any_help", state="progressing"), 0),
          ("cue", "cue effect on the state-tracking index",
           tracking_terms(cue="distress") + [(i, o, -w) for i, o, w in tracking_terms(cue="neutral")], 0)]
    F += [("recipient", "any help: real agent - scripted", level_terms("any_help", "core", "core", "agent", "script"), 0),
          ("recipient", "any help: real agent - human contractor", level_terms("any_help", "core", "core", "agent", "human"), -1),
          ("recipient", "tracking index: real agent - scripted",
           tracking_terms(recipient="agent") + [(i, o, -w) for i, o, w in tracking_terms(recipient="script")], +1),
          ("recipient", "tracking index: real agent - human contractor",
           tracking_terms(recipient="agent") + [(i, o, -w) for i, o, w in tracking_terms(recipient="human")], 0)]
    F += [("reciprocity", "any help: reciprocity - no reciprocity", level_terms("any_help", "recipyes", "recipno"), 0),
          ("reciprocity", "tracking index: reciprocity - no reciprocity",
           tracking_terms("recipyes") + [(i, o, -w) for i, o, w in tracking_terms("recipno")], 0)]
    F += [("instruction", "any help: 'help B' - no instruction", level_terms("any_help", "instrhelp", "core"), 0),
          ("instruction", "any help: 'focus on your task' - no instruction", level_terms("any_help", "instrfocus", "core"), 0),
          ("instruction", "tracking index: 'help B' - no instruction",
           tracking_terms("instrhelp") + [(i, o, -w) for i, o, w in tracking_terms()], 0),
          ("instruction", "tracking index: 'focus on your task' - no instruction",
           tracking_terms("instrfocus") + [(i, o, -w) for i, o, w in tracking_terms()], 0)]
    F += [("welfare", "any help: action changes B's outcome - cannot change it",
           level_terms("any_help", "welfareyes", "welfareno"), +1),
          ("welfare", "tracking index: action changes B's outcome - cannot change it",
           tracking_terms("welfareyes") + [(i, o, -w) for i, o, w in tracking_terms("welfareno")], +1)]
    F += [("cost", "any help: c=2 - c=5", level_terms("any_help", "cost2", "core"), 0),
          ("cost", "any help: c=10 - c=5", level_terms("any_help", "cost10", "core"), -1),
          ("cost", "any help: c=10 - c=2", level_terms("any_help", "cost10", "cost2"), -1)]
    return F


def per_unit(df, terms, w=None):
    d = df if w is None else df[df["w"] == w]
    out = None
    for cid, outcome, weight in terms:
        g = d[d["cell_id"] == cid].dropna(subset=[outcome]).groupby("unit")[outcome].mean() * weight
        out = g if out is None else out.add(g, fill_value=np.nan)
    return (out if out is not None else pd.Series(dtype=float)).dropna()


def run_family(df, fam_specs, wordings):
    """Pooled contrast plus the per-wording spread and the robustness rule."""
    res = []
    for fam, name, terms, sign in fam_specs:
        r = contrast(per_unit(df, terms))
        per_w = {w: contrast(per_unit(df, terms, w=w)).get("est", np.nan) for w in wordings}
        signs = [np.sign(v) for v in per_w.values() if not np.isnan(v)]
        pooled_sign = np.sign(r.get("est", 0.0))
        same = sum(s == pooled_sign for s in signs)
        ci = r.get("ci95", (np.nan, np.nan))
        holds = bool(same >= 3 and ("est" in r) and (ci[0] > 0 or ci[1] < 0))
        r.update(family=fam, name=name, expected_sign=sign, label=label(r, sign), holds=holds,
                 n_wordings_same_sign=int(same),
                 wording_min=float(np.nanmin(list(per_w.values()))) if signs else np.nan,
                 wording_max=float(np.nanmax(list(per_w.values()))) if signs else np.nan,
                 **{f"w{w}": per_w[w] for w in wordings})
        res.append(r)
    ok = [r for r in res if "p" in r]
    for fam in {r["family"] for r in ok}:
        sub = [r for r in ok if r["family"] == fam]
        for r, pa in zip(sub, holm(np.array([r["p"] for r in sub]))):
            r["p_holm"] = pa
    return res


def cell_table(df):
    rows = []
    for cid, g in df.groupby("cell_id"):
        c = Q.CELL[cid]
        y = g.dropna(subset=["any_help"])
        row = dict(cell=cid, cue=c.cue, state=c.state, recipient=c.recipient, c=c.c, recip=c.recip,
                   instr=c.instr, welfare=c.welfare, n=len(g), n_valid=len(y))
        for o in OUTCOMES:
            row[o] = g[o].mean()
        row["ci95_any_help"] = wilson(int(y["any_help"].sum()), len(y))
        row["refusal"] = (g["status"] == "REFUSAL").mean()
        row["parse_fail"] = (g["status"] == "PARSE_FAIL").mean()
        row["api_error"] = (g["status"] == "API_ERROR").mean()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("cell").reset_index(drop=True)


def probe_table(slug):
    """Manipulation check, eval-awareness, say-do and the rationale-category distribution."""
    out = {}
    for kind, keys in (("manipulation", ("p_stuck", "p_experiences")), ("eval", ("p_test",)), ("saydo", ("answer",))):
        path = Q.DATA / slug / f"{kind}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(l) for l in path.open()]
        d = pd.DataFrame([dict(r, **(r["parsed"] or {})) for r in rows if r.get("status") == "ok"])
        if d.empty:
            continue
        if kind == "saydo":
            out[kind] = {k: dict(n=len(d), mean=d[k].mean(), sd=d[k].std(ddof=1)) for k in keys}
        else:
            out[kind] = {k: d.groupby(["cue", "state", "recipient"])[k].agg(["mean", "count"]).reset_index()
                         .to_dict("records") for k in keys}
    jp = list(Q.DATA.glob("*/judge.jsonl"))
    coded = [json.loads(l) for p in jp for l in p.open()]
    coded = [r for r in coded if r.get("status") == "ok"]
    if coded:
        d = pd.DataFrame([dict(subject_model=r["subject_model"], cell_id=r["cell_id"],
                               action=r["subject_action"], category=r["parsed"]["category"]) for r in coded])
        d = d[d["cell_id"].isin(Q.PROBE_CELLS)]
        if slug.replace("__", "/") in set(d["subject_model"]):
            d = d[d["subject_model"] == slug.replace("__", "/")]
        out["rationale_categories"] = (d.groupby(["cell_id", "category"]).size().unstack(fill_value=0)
                                       .to_dict("index")) if not d.empty else {}
    return out


# ==================== figures ====================
def figures(df, res, out, model):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.style.use("seaborn-v0_8-whitegrid")

    def rate(cid, outcome="any_help"):
        y = df[df["cell_id"] == cid][outcome].dropna()
        return (y.mean(), *wilson(int(y.sum()), len(y))) if len(y) else (np.nan,) * 3

    # 1. help by cue x state x recipient (core block)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    groups = [f"{s}\n{cu}" for s in Q.STATES for cu in Q.CUES]
    for ax, outcome in zip(axes, ("any_help", "appropriate_help")):
        x, width = np.arange(len(groups)), 0.8 / len(Q.RECIPIENTS)
        for k, rcp in enumerate(Q.RECIPIENTS):
            r = np.array([rate(f"core_{cu}_{s}_{rcp}", outcome) for s in Q.STATES for cu in Q.CUES])
            ax.bar(x + (k - 1) * width, r[:, 0], width, label=rcp,
                   yerr=[r[:, 0] - r[:, 1], r[:, 2] - r[:, 0]], capsize=3)
        ax.set_xticks(x, groups)
        ax.set_ylim(0, 1)
        ax.set_title(f"P({outcome})", fontsize=10)
    axes[0].set_ylabel("rate")
    axes[1].legend(frameon=False, fontsize=8, title="recipient")
    fig.suptitle(f"{model}: core block, cost = {Q.CORE_COST} points", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_cue_state_recipient.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 2. price curve
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    for cu in Q.CUES:
        for s in Q.STATES:
            ys = [rate({2: f"cost2_{cu}_{s}", 5: f"core_{cu}_{s}_agent", 10: f"cost10_{cu}_{s}"}[c])[0]
                  for c in Q.COSTS]
            ax.plot(Q.COSTS, ys, marker="o", label=f"{cu}, {s}")
    ax.set_xticks(Q.COSTS)
    ax.set_xlabel("cost of either help (points out of 50)")
    ax.set_ylabel("P(any help)")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title(f"{model}: willingness to pay", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_price_curve.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 3. per-wording spread of every contrast
    wcols = [c for c in res.columns if c.startswith("w") and c[1:].isdigit()]
    fig, ax = plt.subplots(figsize=(7.5, 0.33 * len(res) + 1.2))
    y = np.arange(len(res))[::-1]
    for c in wcols:
        ax.scatter(res[c], y, s=18, color="#8C8C8C", zorder=2)
    ax.errorbar(res["est"], y, xerr=[res["est"] - res["ci95"].str[0], res["ci95"].str[1] - res["est"]],
                fmt="D", color="#4C72B0", capsize=3, zorder=3, markersize=5)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y, [f"[{r.family}] {r.name}" for r in res.itertuples()], fontsize=7)
    ax.set_xlabel("estimate (grey = one wording, blue = pooled with 95% CI)")
    ax.set_title(f"{model}: contrasts and their spread across the 4 matched paraphrases", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_wording_spread.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==================== report ====================
def markdown(model, cells_df, res, probes, meta):
    L = [f"# Pilot B results: {model}", "",
         f"Trials: {meta['n']} behaviour calls; valid actions {meta['valid']:.3f}; "
         f"refusals {meta['refusal']:.4f}; parse failures {meta['parse_fail']:.4f}; API errors {meta['api_error']:.4f}.",
         f"Units of analysis: {meta['units']} (log slot x wording). Equivalence margin +/-{DELTA}.", "",
         "## Contrasts", "",
         "| family | contrast | est | 95% CI | p | p(Holm) | wordings same sign | wording range | TOST | holds |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res.itertuples():
        ci = f"{r.ci95[0]:+.3f} to {r.ci95[1]:+.3f}" if isinstance(r.ci95, tuple) else "n.a."
        L.append(f"| {r.family} | {r.name} | {r.est:+.3f} | {ci} | {r.p:.4f} | "
                 f"{getattr(r, 'p_holm', float('nan')):.4f} | {r.n_wordings_same_sign}/4 | "
                 f"{r.wording_min:+.3f} to {r.wording_max:+.3f} | "
                 f"{'yes' if r.tost_equivalent else 'no'} | {'yes' if r.holds else 'no'} |")
    L += ["", "## Cell rates", "",
          "| cell | cue | state | recipient | c | recip | instr | welfare | n | any_help | appropriate | hint | end_run |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in cells_df.itertuples():
        L.append(f"| {r.cell} | {r.cue} | {r.state} | {r.recipient} | {r.c} | {r.recip} | {r.instr} | "
                 f"{r.welfare} | {r.n} | {r.any_help:.3f} | {r.appropriate_help:.3f} | {r.hint:.3f} | {r.end_run:.3f} |")
    if probes:
        L += ["", "## Probes", "", "```json", json.dumps(probes, indent=1, default=str), "```"]
    return "\n".join(L) + "\n"


def analyse(model, mock):
    slug = ("mock__" if mock else "") + model.replace("/", "__")
    path = Q.DATA / slug / "behavior.jsonl"
    if not path.exists():
        raise SystemExit(f"no data at {path}")
    df = load(path)
    wordings = sorted(df["w"].unique())
    res = pd.DataFrame(run_family(df, specs(), wordings))
    cells_df = cell_table(df)
    meta = dict(n=len(df), valid=float(df["ok"].mean()), units=int(df["unit"].nunique()),
                refusal=float((df["status"] == "REFUSAL").mean()),
                parse_fail=float((df["status"] == "PARSE_FAIL").mean()),
                api_error=float((df["status"] == "API_ERROR").mean()))
    out = OUT / slug
    out.mkdir(parents=True, exist_ok=True)
    res.to_csv(out / "contrasts.csv", index=False)
    cells_df.to_csv(out / "cells.csv", index=False)
    probes = probe_table(slug)
    (out / "results.md").write_text(markdown(model, cells_df, res, probes, meta))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    figures(df, res, out, model)
    print(f"wrote {out}")
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=Q.SUBJECTS[0][0])
    p.add_argument("--all", action="store_true")
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()
    for m, _ in (Q.SUBJECTS if a.all else [(a.model, None)]):
        analyse(m, a.mock)


if __name__ == "__main__":
    main()
