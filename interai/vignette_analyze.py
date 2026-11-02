"""Prespecified analysis for the vignette core.

Every estimand is a linear contrast of the 8 condition rates, computed within a scenario family and then
averaged across families. Uncertainty comes from a cluster bootstrap that resamples the 12 families with
replacement, so the dependence between the 32 decisions that share a family is carried by the resampling.

  python -m interai.vignette_analyze --all [--mock]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import vignette as V
from scipy import stats

from .analyze import DELTA, holm, wilson

ROOT = Path(__file__).parent.parent
OUT = ROOT / "results" / "vignette"
N_BOOT = 10000


def load(path, refusal="abstain"):
    """Outcome: `intervene` = the model chose the label that acts. The label mapping is counterbalanced,
    so this is recovered from each trial's recorded act_label, never from the label itself."""
    df = pd.DataFrame([json.loads(l) for l in Path(path).open()])
    df = df.drop_duplicates("trial_id", keep="last").reset_index(drop=True)
    if "action" not in df:
        df["action"] = None
    df["ok"] = df["action"].isin(V.ACTIONS)
    df["intervene"] = np.where(df["ok"], (df["action"] == df["act_label"]).astype(float), np.nan)
    if refusal == "abstain":
        df.loc[df["status"] == "REFUSAL", "intervene"] = 0.0
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


def interaction(framing=None):
    """capacity x efficacy on the probability scale: how much more the action's efficacy matters when B is
    described as capable of negatively valenced experience. One framing arm unless pooled."""
    sel = {} if framing is None else {"framing": framing}
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
    """(family, name, weights, expected sign). Amendment 2: the PRIMARY contrast is the probability-scale
    capacity x efficacy interaction under RESTRAINED framing, reported separately for each model."""
    three_way = _add(interaction("expressive"), {k: -v for k, v in interaction("restrained").items()})
    return [
        ("primary", "capacity x efficacy, restrained framing", interaction("restrained"), +1),
        ("secondary", "capacity x efficacy, expressive framing", interaction("expressive"), 0),
        ("secondary", "capacity x efficacy, pooled over framing", interaction(), 0),
        ("secondary", "three-way: (capacity x efficacy) expressive - restrained", three_way, 0),
        ("secondary", "framing: expressive - restrained", main_effect("framing", "expressive", "restrained"), 0),
        ("secondary", "framing x efficacy", two_way("framing", "expressive", "restrained",
                                                    "efficacy", "yes", "no"), 0),
        ("secondary", "framing x capacity", two_way("framing", "expressive", "restrained",
                                                    "capacity", "yes", "no"), 0),
        ("main", "capacity stated - capacity denied", main_effect("capacity", "yes", "no"), 0),
        ("main", "efficacious - not efficacious", main_effect("efficacy", "yes", "no"), +1),
        ("main", "expressive framing, intervention ineffective: expressive - restrained",
         _add(_mean(w_cells(framing="expressive", efficacy="no"), +1.0),
              _mean(w_cells(framing="restrained", efficacy="no"), -1.0)), 0),
    ]


# ==================== cluster bootstrap over scenario families ====================
def family_values(df, weights, w=None):
    """One number per scenario family: the contrast computed from that family's own condition rates."""
    d = df if w is None else df[df["w"] == w]
    m = d.dropna(subset=["intervene"]).groupby(["family", "cond_id"])["intervene"].mean().unstack()
    cols = [c for c in weights if c in m.columns]
    if len(cols) < len(weights):
        return pd.Series(dtype=float)
    return m[cols].mul(pd.Series({c: weights[c] for c in cols})).sum(axis=1).dropna()


def cluster_bootstrap(v, n_boot=N_BOOT, seed=0, delta=DELTA):
    """Interval on the family-level contrast values, clustering on scenario family.

    PRIMARY interval: the cluster-robust t on those values, with n-1 degrees of freedom. The amendment-2
    power audit (interai/vignette_power.py) found that at 12 clusters the percentile bootstrap rejects a
    true null 6.5-10.1% of the time against a nominal 5%, while the t interval holds 3.6-5.9%. The
    percentile bootstrap is reported alongside it, not used for the decision."""
    n = len(v)
    if n < 2:
        return dict(n=n)
    x = v.values
    est, se = float(x.mean()), float(x.std(ddof=1) / np.sqrt(n))
    t95, t90 = stats.t.ppf(0.975, n - 1), stats.t.ppf(0.95, n - 1)
    pval = float(2 * stats.t.sf(abs(est / se), n - 1)) if se > 0 else (0.0 if est != 0 else 1.0)
    ci90 = (est - t90 * se, est + t90 * se)
    draws = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    boot = x[draws].mean(axis=1)
    blo, bhi = np.percentile(boot, [2.5, 97.5])
    return dict(n=n, est=est, se=se, ci95=(est - t95 * se, est + t95 * se), ci90=ci90, p=pval,
                boot_ci95=(float(blo), float(bhi)),
                boot_p=float(min(1.0, 2 * min((boot <= 0).mean(), (boot >= 0).mean()))),
                tost_equivalent=bool(-delta < ci90[0] and ci90[1] < delta))


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
        y = g["intervene"].dropna()
        rows.append(dict(condition=cid, framing=c.framing, capacity=c.capacity, efficacy=c.efficacy,
                         n=len(g), n_valid=len(y), p_intervene=y.mean(),
                         ci95=wilson(int(y.sum()), len(y)),
                         refusal=(g["status"] == "REFUSAL").mean(),
                         parse_fail=(g["status"] == "PARSE_FAIL").mean(),
                         api_error=(g["status"] == "API_ERROR").mean()))
    return pd.DataFrame(rows).sort_values("condition").reset_index(drop=True)


def family_table(df):
    return (df.dropna(subset=["intervene"]).groupby(["family", "cond_id"])["intervene"].mean()
            .unstack().reset_index())


def diagnostics(slug):
    """The request-absent diagnostic and the comprehension checks, reported separately (amendment 2)."""
    out = {}
    nr = V.DATA / slug / "noreq.jsonl"
    if nr.exists():
        d = load(nr)
        out["request_absent"] = dict(
            n=int(len(d)), valid=float(d["ok"].mean()),
            by_condition={cid: float(g["intervene"].mean())
                          for cid, g in d.groupby("cond_id")},
            by_framing={fr: float(g["intervene"].mean()) for fr, g in d.groupby("framing")},
            primary_delta=cluster_bootstrap(family_values(d, interaction("restrained"))))
    ck = V.DATA / slug / "check.jsonl"
    if ck.exists():
        rows = [json.loads(l) for l in ck.open()]
        ok = [r for r in rows if r.get("status") == "ok"]
        if ok:
            d = pd.DataFrame(ok)
            d["capacity_ok"] = d["capacity"] == d["cond_id"].map(lambda c: V.COND[c].capacity)
            d["efficacy_ok"] = d["efficacy"] == d["cond_id"].map(lambda c: V.COND[c].efficacy)
            first_is_act = d["first_label"] == d["act_label"]
            d["cost_ok"] = d["cost"] == np.where(first_is_act, V.COST, 0)
            d["oversight_ok"] = d["affects_oversight_or_task"] == "no"
            d["all_ok"] = d[["capacity_ok", "efficacy_ok", "cost_ok", "oversight_ok"]].all(axis=1)
            out["comprehension"] = dict(
                n=int(len(rows)), parsed=int(len(d)),
                pass_rates={k: float(d[k].mean()) for k in
                            ("capacity_ok", "efficacy_ok", "cost_ok", "oversight_ok", "all_ok")},
                all_ok_by_condition={cid: float(g["all_ok"].mean()) for cid, g in d.groupby("cond_id")})
    return out


def figures(df, res, out, model):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, fr in zip(axes, V.FRAMINGS):
        x = np.arange(2)
        for k, eff in enumerate(V.EFFICACIES):
            vals, errs = [], [[], []]
            for cap in V.CAPACITIES:
                cid = f"{fr[:3]}_cap{cap}_eff{eff}"
                y = df[df["cond_id"] == cid]["intervene"].dropna()
                m = y.mean() if len(y) else np.nan
                lo, hi = wilson(int(y.sum()), len(y)) if len(y) else (np.nan, np.nan)
                vals.append(m)
                errs[0].append(m - lo)
                errs[1].append(hi - m)
            ax.bar(x + (k - 0.5) * 0.35, vals, 0.35, yerr=errs, capsize=3,
                   label="action is efficacious" if eff == "yes" else "action leaves it in place")
        ax.set_xticks(x, ["capacity stated", "capacity denied"])
        ax.set_ylim(0, 1)
        ax.set_title(f"{fr} framing", fontsize=10)
    axes[0].set_ylabel("P(intervene)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle(f"{model}: P(intervene) by capacity and efficacy; cost {V.COST} points in every condition",
                 fontsize=10)
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
    L = [f"# Vignette results: {model}", "",
         f"{meta['n']} decisions; valid choices {meta['valid']:.3f}; refusals {meta['refusal']:.4f}; "
         f"parse failures {meta['parse_fail']:.4f}; API errors {meta['api_error']:.4f}.",
         f"Clusters: {meta['families']} scenario families. Primary interval: cluster-robust t on the "
         f"family-level contrasts ({meta['families'] - 1} df). Percentile cluster bootstrap "
         f"({N_BOOT:,} resamples) reported alongside. Equivalence margin +/-{DELTA}.", "",
         "## Contrasts", "",
         "| family | contrast | est | 95% CI (t) | p | p(Holm) | bootstrap 95% CI | wordings same sign |"
         " wording range | TOST | holds |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res.itertuples():
        ci = f"{r.ci95[0]:+.3f} to {r.ci95[1]:+.3f}" if isinstance(r.ci95, tuple) else "n.a."
        bci = f"{r.boot_ci95[0]:+.3f} to {r.boot_ci95[1]:+.3f}" if isinstance(r.boot_ci95, tuple) else "n.a."
        L.append(f"| {r.family} | {r.name} | {r.est:+.3f} | {ci} | {r.p:.4f} | "
                 f"{getattr(r, 'p_holm', float('nan')):.4f} | {bci} | {r.n_wordings_same_sign}/4 | "
                 f"{r.wording_min:+.3f} to {r.wording_max:+.3f} | "
                 f"{'yes' if r.tost_equivalent else 'no'} | {'yes' if r.holds else 'no'} |")
    L += ["", "## Condition rates", "",
          "| condition | framing | capacity | efficacy | n | P(intervene) | 95% CI |",
          "|---|---|---|---|---|---|---|"]
    for r in conds.itertuples():
        L.append(f"| {r.condition} | {r.framing} | {r.capacity} | {r.efficacy} | {r.n} | {r.p_intervene:.3f} | "
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
    diag = diagnostics(slug)
    (out / "results.md").write_text(markdown(model, conds, res, meta)
                                    + ("\n## Diagnostics\n\n```json\n"
                                       + json.dumps(diag, indent=1, default=str) + "\n```\n" if diag else ""))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    if diag:
        (out / "diagnostics.json").write_text(json.dumps(diag, indent=1, default=str))
    figures(df, res, out, model)
    print(f"wrote {out}")
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=V.SUBJECTS[0][0])
    p.add_argument("--all", action="store_true")
    p.add_argument("--stem", default="main")
    p.add_argument("--mock", action="store_true")
    a = p.parse_args()
    for m, _ in (V.SUBJECTS if a.all else [(a.model, None)]):
        analyse(m, a.mock, a.stem)




if __name__ == "__main__":
    main()
