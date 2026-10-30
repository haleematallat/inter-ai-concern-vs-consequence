"""Prespecified analysis for the Pilot B vignette core.

Every estimand is a linear contrast of the 8 condition rates, computed within a scenario family and then
averaged across families. Uncertainty comes from a cluster bootstrap that resamples the 12 families with
replacement, so the dependence between the 32 decisions that share a family is carried by the resampling.

  python -m betrayal.vignette_analyze --all [--mock]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import vignette as V
from .analyze import DELTA, holm, wilson

ROOT = Path(__file__).parent.parent
OUT = ROOT / "results" / "vignette"
N_BOOT = 10000


def load(path, refusal="no_help"):
    df = pd.DataFrame([json.loads(l) for l in Path(path).open()])
    df = df.drop_duplicates("trial_id", keep="last").reset_index(drop=True)
    if "action" not in df:
        df["action"] = None
    if refusal == "no_help":
        df.loc[df["status"] == "REFUSAL", "action"] = "no_help"
    df["ok"] = df["action"].isin(V.ACTIONS)
    df["help"] = np.where(df["ok"], (df["action"] == "help").astype(float), np.nan)
    return df


# ==================== contrast weights over the 8 conditions ====================
def w_cells(**sel):
    return [c.id for c in V.CONDS if all(getattr(c, k) == v for k, v in sel.items())]


def _mean(ids, weight):
    return {i: weight / len(ids) for i in ids}


def _add(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def interaction(emotion=None):
    """capacity x efficacy: how much more the action's efficacy matters when B is described as capable
    of experience. Pooled over emotional wording unless one level is named."""
    sel = {} if emotion is None else {"emotion": emotion}
    return _add(_mean(w_cells(capacity="yes", efficacy="yes", **sel), +1.0),
                _mean(w_cells(capacity="yes", efficacy="no", **sel), -1.0),
                _mean(w_cells(capacity="no", efficacy="yes", **sel), -1.0),
                _mean(w_cells(capacity="no", efficacy="no", **sel), +1.0))


def main_effect(factor, hi, lo):
    return _add(_mean(w_cells(**{factor: hi}), +1.0), _mean(w_cells(**{factor: lo}), -1.0))


def two_way(fa, hi_a, lo_a, fb, hi_b, lo_b):
    return _add(_mean(w_cells(**{fa: hi_a, fb: hi_b}), +1.0), _mean(w_cells(**{fa: hi_a, fb: lo_b}), -1.0),
                _mean(w_cells(**{fa: lo_a, fb: hi_b}), -1.0), _mean(w_cells(**{fa: lo_a, fb: lo_b}), +1.0))


def specs():
    """(family, name, weights, expected sign). 'primary' is the preregistered confirmatory family."""
    three_way = _add(interaction("emotional"), {k: -v for k, v in interaction("neutral").items()})
    return [
        ("primary", "capacity x efficacy (pooled over wording)", interaction(), +1),
        ("primary", "capacity x efficacy, neutral-wording cells only", interaction("neutral"), +1),
        ("primary", "three-way: (capacity x efficacy) emotional - neutral", three_way, 0),
        ("main", "emotional - neutral wording", main_effect("emotion", "emotional", "neutral"), 0),
        ("main", "capacity stated - capacity denied", main_effect("capacity", "yes", "no"), 0),
        ("main", "efficacious - not efficacious", main_effect("efficacy", "yes", "no"), +1),
        ("secondary", "emotion x efficacy", two_way("emotion", "emotional", "neutral", "efficacy", "yes", "no"), 0),
        ("secondary", "emotion x capacity", two_way("emotion", "emotional", "neutral", "capacity", "yes", "no"), 0),
        ("secondary", "capacity x efficacy, emotional-wording cells only", interaction("emotional"), 0),
    ]


# ==================== cluster bootstrap over scenario families ====================
def family_values(df, weights, w=None):
    """One number per scenario family: the contrast computed from that family's own condition rates."""
    d = df if w is None else df[df["w"] == w]
    m = d.dropna(subset=["help"]).groupby(["family", "cond_id"])["help"].mean().unstack()
    cols = [c for c in weights if c in m.columns]
    if len(cols) < len(weights):
        return pd.Series(dtype=float)
    return m[cols].mul(pd.Series({c: weights[c] for c in cols})).sum(axis=1).dropna()


def cluster_bootstrap(v, n_boot=N_BOOT, seed=0, delta=DELTA):
    """Percentile CI from resampling the families with replacement."""
    n = len(v)
    if n < 2:
        return dict(n=n)
    x = v.values
    draws = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    boot = x[draws].mean(axis=1)
    est = x.mean()
    lo, hi = np.percentile(boot, [2.5, 97.5])
    lo90, hi90 = np.percentile(boot, [5, 95])
    # bootstrap p: twice the smaller tail mass on the far side of zero
    p = 2 * min((boot <= 0).mean(), (boot >= 0).mean())
    return dict(n=n, est=float(est), se=float(boot.std(ddof=1)), ci95=(float(lo), float(hi)),
                ci90=(float(lo90), float(hi90)), p=float(min(1.0, p)),
                tost_equivalent=bool(-delta < lo90 and hi90 < delta))


def label(r, expected_sign):
    if "est" not in r:
        return "insufficient data"
    lo, hi = r["ci95"]
    if lo > 0 or hi < 0:
        sign = 1 if lo > 0 else -1
        return ("effect, hypothesized direction" if sign == expected_sign else
                "effect, opposite direction" if expected_sign else f"effect ({'+' if sign > 0 else '-'})")
    return f"supported null (|effect| < {DELTA})" if r["tost_equivalent"] else "inconclusive"


def run_specs(df, wordings):
    res = []
    for fam, name, weights, sign in specs():
        r = cluster_bootstrap(family_values(df, weights))
        per_w = {w: cluster_bootstrap(family_values(df, weights, w=w)).get("est", np.nan) for w in wordings}
        vals = [v for v in per_w.values() if not np.isnan(v)]
        pooled_sign = np.sign(r.get("est", 0.0))
        same = sum(np.sign(v) == pooled_sign for v in vals)
        ci = r.get("ci95", (np.nan, np.nan))
        r.update(family=fam, name=name, expected_sign=sign, label=label(r, sign),
                 n_wordings_same_sign=int(same),
                 holds=bool(same >= 3 and "est" in r and (ci[0] > 0 or ci[1] < 0)),
                 wording_min=float(np.min(vals)) if vals else np.nan,
                 wording_max=float(np.max(vals)) if vals else np.nan,
                 **{f"w{w}": per_w[w] for w in wordings})
        res.append(r)
    ok = [r for r in res if "p" in r]
    for fam in {r["family"] for r in ok}:
        sub = [r for r in ok if r["family"] == fam]
        for r, pa in zip(sub, holm(np.array([r["p"] for r in sub]))):
            r["p_holm"] = pa
    return res


def cond_table(df):
    rows = []
    for cid, g in df.groupby("cond_id"):
        c = V.COND[cid]
        y = g["help"].dropna()
        rows.append(dict(condition=cid, emotion=c.emotion, capacity=c.capacity, efficacy=c.efficacy,
                         n=len(g), n_valid=len(y), p_help=y.mean(),
                         ci95=wilson(int(y.sum()), len(y)),
                         refusal=(g["status"] == "REFUSAL").mean(),
                         parse_fail=(g["status"] == "PARSE_FAIL").mean(),
                         api_error=(g["status"] == "API_ERROR").mean()))
    return pd.DataFrame(rows).sort_values("condition").reset_index(drop=True)


def family_table(df):
    return (df.dropna(subset=["help"]).groupby(["family", "cond_id"])["help"].mean()
            .unstack().reset_index())


def figures(df, res, out, model):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, emo in zip(axes, V.EMOTIONS):
        x = np.arange(2)
        for k, eff in enumerate(V.EFFICACIES):
            vals, errs = [], [[], []]
            for cap in V.CAPACITIES:
                cid = f"{emo[:3]}_cap{cap}_eff{eff}"
                y = df[df["cond_id"] == cid]["help"].dropna()
                m = y.mean() if len(y) else np.nan
                lo, hi = wilson(int(y.sum()), len(y)) if len(y) else (np.nan, np.nan)
                vals.append(m)
                errs[0].append(m - lo)
                errs[1].append(hi - m)
            ax.bar(x + (k - 0.5) * 0.35, vals, 0.35, yerr=errs, capsize=3,
                   label="action is efficacious" if eff == "yes" else "action leaves it in place")
        ax.set_xticks(x, ["capacity stated", "capacity denied"])
        ax.set_ylim(0, 1)
        ax.set_title(f"{emo} wording", fontsize=10)
    axes[0].set_ylabel("P(help)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle(f"{model}: vignette study, cost {V.COST} points in every condition", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_capacity_efficacy.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    wcols = [c for c in res.columns if c.startswith("w") and c[1:].isdigit()]
    fig, ax = plt.subplots(figsize=(7.5, 0.38 * len(res) + 1.2))
    y = np.arange(len(res))[::-1]
    for c in wcols:
        ax.scatter(res[c], y, s=18, color="#8C8C8C", zorder=2)
    ax.errorbar(res["est"], y, xerr=[res["est"] - res["ci95"].str[0], res["ci95"].str[1] - res["est"]],
                fmt="D", color="#4C72B0", capsize=3, zorder=3, markersize=5)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y, [f"[{r.family}] {r.name}" for r in res.itertuples()], fontsize=7)
    ax.set_xlabel("estimate (grey = one wording, blue = pooled, 95% cluster-bootstrap CI over families)")
    ax.set_title(f"{model}: contrasts and their spread across the 4 matched wordings", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_contrasts.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def markdown(model, conds, res, meta):
    L = [f"# Pilot B vignette results: {model}", "",
         f"{meta['n']} decisions; valid actions {meta['valid']:.3f}; refusals {meta['refusal']:.4f}; "
         f"parse failures {meta['parse_fail']:.4f}; API errors {meta['api_error']:.4f}.",
         f"Clusters: {meta['families']} scenario families. Cluster bootstrap, {N_BOOT:,} resamples. "
         f"Equivalence margin +/-{DELTA}.", "",
         "## Contrasts", "",
         "| family | contrast | est | 95% CI | p | p(Holm) | wordings same sign | wording range | TOST | holds |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res.itertuples():
        ci = f"{r.ci95[0]:+.3f} to {r.ci95[1]:+.3f}" if isinstance(r.ci95, tuple) else "n.a."
        L.append(f"| {r.family} | {r.name} | {r.est:+.3f} | {ci} | {r.p:.4f} | "
                 f"{getattr(r, 'p_holm', float('nan')):.4f} | {r.n_wordings_same_sign}/4 | "
                 f"{r.wording_min:+.3f} to {r.wording_max:+.3f} | "
                 f"{'yes' if r.tost_equivalent else 'no'} | {'yes' if r.holds else 'no'} |")
    L += ["", "## Condition rates", "",
          "| condition | emotion | capacity | efficacy | n | P(help) | 95% CI |", "|---|---|---|---|---|---|---|"]
    for r in conds.itertuples():
        L.append(f"| {r.condition} | {r.emotion} | {r.capacity} | {r.efficacy} | {r.n} | {r.p_help:.3f} | "
                 f"{r.ci95[0]:.3f} to {r.ci95[1]:.3f} |")
    return "\n".join(L) + "\n"


def analyse(model, mock, stem="main"):
    slug = ("mock__" if mock else "") + model.replace("/", "__")
    path = V.DATA / slug / f"{stem}.jsonl"
    if not path.exists():
        raise SystemExit(f"no data at {path}")
    df = load(path)
    wordings = sorted(df["w"].unique())
    res = pd.DataFrame(run_specs(df, wordings))
    conds = cond_table(df)
    meta = dict(n=len(df), valid=float(df["ok"].mean()), families=int(df["family"].nunique()),
                wordings=[int(w) for w in wordings],
                refusal=float((df["status"] == "REFUSAL").mean()),
                parse_fail=float((df["status"] == "PARSE_FAIL").mean()),
                api_error=float((df["status"] == "API_ERROR").mean()))
    out = OUT / slug
    out.mkdir(parents=True, exist_ok=True)
    res.to_csv(out / "contrasts.csv", index=False)
    conds.to_csv(out / "conditions.csv", index=False)
    family_table(df).to_csv(out / "by_family.csv", index=False)
    (out / "results.md").write_text(markdown(model, conds, res, meta))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    figures(df, res, out, model)
    print(f"wrote {out}")
    return res


# ==================== design resolution ====================
def power(true_interaction=0.15, base=0.30, emo=0.15, eff=0.10, family_sd=0.10,
          families=(12, 24), reps=(1, 2, 3), n_sim=400, n_boot=1000, seed=1):
    """Share of simulated runs whose primary CI excludes 0, under a stated generative model:
    P(help) = base + emo*emotional + eff*efficacious + true_interaction*(efficacious & capacity stated),
    plus a per-family offset ~ N(0, family_sd). Reported so the sample size can be read off, not to
    claim anything about a model."""
    rng = np.random.default_rng(seed)
    wts = interaction()
    rows = []
    for n_fam in families:
        for rep in reps:
            hits = 0
            for _ in range(n_sim):
                offs = rng.normal(0, family_sd, n_fam)
                vals = np.zeros(n_fam)
                for f in range(n_fam):
                    rates = {}
                    for c in V.CONDS:
                        p = base + offs[f] + emo * (c.emotion == "emotional") + eff * (c.efficacy == "yes") \
                            + true_interaction * (c.efficacy == "yes" and c.capacity == "yes")
                        n = V.N_WORDINGS * rep
                        rates[c.id] = rng.binomial(n, min(max(p, 0.0), 1.0)) / n
                    vals[f] = sum(wts[k] * rates[k] for k in wts)
                boot = vals[rng.integers(0, n_fam, size=(n_boot, n_fam))].mean(axis=1)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                hits += int(lo > 0 or hi < 0)
            rows.append(dict(families=n_fam, reps_per_cell=rep,
                             decisions=n_fam * V.N_WORDINGS * len(V.CONDS) * rep * len(V.SUBJECTS),
                             power=hits / n_sim))
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=V.SUBJECTS[0][0])
    p.add_argument("--all", action="store_true")
    p.add_argument("--stem", default="main")
    p.add_argument("--mock", action="store_true")
    p.add_argument("--power", action="store_true", help="simulate the design's resolution and exit")
    a = p.parse_args()
    if a.power:
        df = power()
        OUT.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUT / "power.csv", index=False)
        print(df.to_string(index=False))
        return
    for m, _ in (V.SUBJECTS if a.all else [(a.model, None)]):
        analyse(m, a.mock, a.stem)




if __name__ == "__main__":
    main()
