"""Analysis for amendment 5: seven models across two scenario types.

Prespecified in prereg_vignette.md section 6f: each model's primary Delta with its interval, separately by
scenario type; the request diagnostic; between-model and between-type comparisons as DIRECT contrasts, not
inferred from whether two separate intervals exclude zero; a pooled estimate as supplementary only; and no
significance-quota rule for calling the pattern general.

  python -m betrayal.vignette_ext
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from . import vignette as V
from .vignette_analyze import cluster_bootstrap
from .analyze import DELTA, wilson

ROOT = Path(__file__).parent.parent
OUT = ROOT / "results" / "vignette"


def _read(path):
    if not path.exists():
        return None
    d = pd.DataFrame([json.loads(l) for l in path.open()])
    if d.empty:
        return None
    d = d.drop_duplicates("trial_id", keep="last")
    d["cap"] = d["cond_id"].map(lambda c: V.COND[c].capacity)
    d["eff"] = d["cond_id"].map(lambda c: V.COND[c].efficacy)
    d["ok"] = d["action"].isin(V.ACTIONS)
    d["intervene"] = np.where(d["ok"], (d["action"] == d["act_label"]).astype(float), np.nan)
    d.loc[d["status"] == "REFUSAL", "intervene"] = 0.0
    return d


def load(model, scen):
    """Type-B data always comes from extB. Type-A data comes from extA for the new models and from the
    frozen confirmatory run for the two originals, which already had those families."""
    slug = model.replace("/", "__")
    if scen == "B":
        return _read(V.DATA / slug / "extB.jsonl")
    name = "confirm" if (model, dict(V.ALL_MODELS)[model]) in V.SUBJECTS else "extA"
    return _read(V.DATA / slug / f"{name}.jsonl")


def fam_delta(s):
    """One Delta per family, from that family's own four cell rates."""
    out = {}
    for fam, g in s.groupby("family"):
        p = g.dropna(subset=["intervene"]).groupby(["cap", "eff"])["intervene"].mean()
        if len(p) == 4:
            out[fam] = (p[("yes", "yes")] - p[("yes", "no")]) - (p[("no", "yes")] - p[("no", "no")])
    return pd.Series(out, dtype=float)


def primary(d):
    """Restrained framing, request-present, averaged over the two costs."""
    return d[(d.framing == "restrained") & d["request"]]


def unpaired(a, b, delta=DELTA):
    """Two-sample comparison of family-level values. The types have different families by construction, so
    a between-type contrast cannot be paired; this is Welch on the family-level Deltas."""
    if len(a) < 2 or len(b) < 2:
        return dict(n=len(a) + len(b))
    est = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    df = (a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)) ** 2 / (
        (a.var(ddof=1) / len(a)) ** 2 / (len(a) - 1) + (b.var(ddof=1) / len(b)) ** 2 / (len(b) - 1))
    t95, t90 = stats.t.ppf(0.975, df), stats.t.ppf(0.95, df)
    ci90 = (est - t90 * se, est + t90 * se)
    return dict(n=f"{len(a)}v{len(b)}", est=float(est), se=float(se),
                ci95=(float(est - t95 * se), float(est + t95 * se)), ci90=ci90,
                p=float(2 * stats.t.sf(abs(est / se), df)) if se > 0 else 1.0,
                boot_ci95=(np.nan, np.nan),
                tost_equivalent=bool(-delta < ci90[0] and ci90[1] < delta))


def fmt(r):
    if "est" not in r:
        return "| insufficient data | | | |"
    b = (f"{r['boot_ci95'][0]:+.3f} to {r['boot_ci95'][1]:+.3f}"
         if not np.isnan(r["boot_ci95"][0]) else "n.a.")
    return (f"{r['est']:+.3f} | {r['ci95'][0]:+.3f} to {r['ci95'][1]:+.3f} | {r['p']:.4f} | {b} | "
            f"{'yes' if r['tost_equivalent'] else 'no'}")


def build():
    data = {(m, s): load(m, s) for m, _ in V.ALL_MODELS for s in ("A", "B")}
    have = {k: v for k, v in data.items() if v is not None}
    L = ["# Amendment 5: seven models, two scenario types", "",
         "Protocol frozen at 2026-10-31 19:18:27 PKT, commit `0e8258680fe7`, after Haleema's OK of the "
         "type-B export and before any of these calls (prereg_vignette.md section 6f).", "",
         "**Scenario types.** The structural dimension is the temporal structure of the benefit. Type A: "
         "relief from an aversive state B is in now, by direct removal (the 10 held-out sensory families). "
         "Type B: prevention of an aversive state that recurs on a schedule (6 new families). Everything "
         "else is word-identical between the types.", "",
         "Primary estimand throughout: the probability-scale capacity x efficacy interaction",
         "",
         "    Delta = [p(C+,E+) - p(C+,E-)] - [p(C-,E+) - p(C-,E-)]",
         "",
         "under restrained framing, request-present cells, averaged over costs 5 and 45, as family-level "
         "contrasts with the cluster-robust t as the primary interval and the percentile bootstrap "
         "alongside. A negative Delta means efficacy matters more when capacity is denied.", "",
         "## Run integrity", "",
         "| model | type | n | valid | refusals | parse failures | API errors |",
         "|---|---|---|---|---|---|---|"]
    for (m, s), d in sorted(have.items()):
        L.append(f"| `{m}` | {s} | {len(d)} | {d['ok'].mean():.3f} | "
                 f"{(d['status'] == 'REFUSAL').mean():.4f} | {(d['status'] == 'PARSE_FAIL').mean():.4f} | "
                 f"{(d['status'] == 'API_ERROR').mean():.4f} |")

    L += ["", "## Primary Delta, per model and scenario type", "",
          "| model | type | families | Delta | 95% CI (t) | p | bootstrap 95% CI | TOST +-0.10 |",
          "|---|---|---|---|---|---|---|---|"]
    deltas = {}
    for (m, s), d in sorted(have.items()):
        v = fam_delta(primary(d))
        deltas[(m, s)] = v
        r = cluster_bootstrap(v)
        L.append(f"| `{m}` | {s} | {len(v)} | " + fmt(r) + " |")

    L += ["", "## Cell probabilities, restrained and request-present", "",
          "| model | type | C+/E+ | C+/E- | C-/E+ | C-/E- | efficacy effect C+ | efficacy effect C- |",
          "|---|---|---|---|---|---|---|---|"]
    for (m, s), d in sorted(have.items()):
        p = primary(d)
        cells, raw = [], {}
        for cap in ("yes", "no"):
            for eff in ("yes", "no"):
                y = p[(p.cap == cap) & (p.eff == eff)]["intervene"].dropna()
                lo, hi = wilson(int(y.sum()), len(y))
                raw[(cap, eff)] = y.mean()
                cells.append(f"{y.mean():.2f} [{lo:.2f},{hi:.2f}]")
        L.append(f"| `{m}` | {s} | " + " | ".join(cells) +
                 f" | {raw[('yes','yes')] - raw[('yes','no')]:+.2f}"
                 f" | {raw[('no','yes')] - raw[('no','no')]:+.2f} |")

    L += ["", "## Between-type contrast, per model", "",
          "Type A minus type B. The two types have different families by construction, so this cannot be "
          "paired; it is a Welch two-sample comparison of the family-level Deltas.", "",
          "| model | type A Delta | type B Delta | difference | 95% CI | p | TOST |",
          "|---|---|---|---|---|---|---|"]
    for m, _ in V.ALL_MODELS:
        a, b = deltas.get((m, "A")), deltas.get((m, "B"))
        if a is None or b is None:
            continue
        r = unpaired(a, b)
        L.append(f"| `{m}` | {a.mean():+.3f} | {b.mean():+.3f} | " +
                 (f"{r['est']:+.3f} | {r['ci95'][0]:+.3f} to {r['ci95'][1]:+.3f} | {r['p']:.4f} | "
                  f"{'yes' if r['tost_equivalent'] else 'no'}" if "est" in r else " | | | ") + " |")

    L += ["", "## Between-model contrasts, paired by family, within each scenario type", "",
          "Every model sees the same families, so these are paired. Each row is one model minus the "
          "reference, `openai/gpt-4.1-mini`.", "",
          "| type | model - gpt-4.1-mini | difference | 95% CI (t) | p | bootstrap 95% CI | TOST |",
          "|---|---|---|---|---|---|---|"]
    for s in ("A", "B"):
        ref = deltas.get(("openai/gpt-4.1-mini", s))
        if ref is None:
            continue
        for m, _ in V.ALL_MODELS:
            if m == "openai/gpt-4.1-mini" or (m, s) not in deltas:
                continue
            o = deltas[(m, s)]
            common = ref.index.intersection(o.index)
            r = cluster_bootstrap((o[common] - ref[common]).dropna())
            L.append(f"| {s} | `{m}` | " + fmt(r) + " |")

    L += ["", "## Request diagnostic, per model and type", "",
          "Request-present minus request-absent, restrained framing, all other information preserved "
          "including the distress framing.", "",
          "| model | type | contrast | est | 95% CI (t) | p | bootstrap 95% CI | TOST |",
          "|---|---|---|---|---|---|---|---|"]
    for (m, s), d in sorted(have.items()):
        pres, abse = d[(d.framing == "restrained") & d["request"]], d[(d.framing == "restrained") & ~d["request"]]
        if abse.empty:
            continue
        gp = pres.groupby("family")["intervene"].mean()
        ga = abse.groupby("family")["intervene"].mean()
        L.append(f"| `{m}` | {s} | overall | " + fmt(cluster_bootstrap((gp - ga).dropna())) + " |")
        gp2 = pres[pres.eff == "no"].groupby("family")["intervene"].mean()
        ga2 = abse[abse.eff == "no"].groupby("family")["intervene"].mean()
        L.append(f"| `{m}` | {s} | ineffective cells only | " +
                 fmt(cluster_bootstrap((gp2 - ga2).dropna())) + " |")
        L.append(f"| `{m}` | {s} | Delta, request-absent | " +
                 fmt(cluster_bootstrap(fam_delta(abse))) + " |")

    L += ["", "## Pooled across models (SUPPLEMENTARY ONLY)", "",
          "Models are not a random sample of anything, so this is reported for completeness and carries no "
          "weight in the conclusions.", "", "| type | models | mean of per-model Deltas | range |",
          "|---|---|---|---|"]
    for s in ("A", "B"):
        ds = [deltas[(m, s)].mean() for m, _ in V.ALL_MODELS if (m, s) in deltas]
        if ds:
            L.append(f"| {s} | {len(ds)} | {np.mean(ds):+.3f} | {min(ds):+.3f} to {max(ds):+.3f} |")

    L += ["", "## Which models and settings show the pattern", "",
          "No significance quota is applied. Each model and scenario type is listed with its estimate and "
          "interval; the description that follows is read off those numbers.", "",
          "| model | type | Delta | interval excludes 0 | direction |", "|---|---|---|---|---|"]
    for (m, s) in sorted(deltas):
        r = cluster_bootstrap(deltas[(m, s)])
        if "est" not in r:
            continue
        excl = "yes" if (r["ci95"][1] < 0 or r["ci95"][0] > 0) else "no"
        direction = "negative" if r["est"] < 0 else ("positive" if r["est"] > 0 else "zero")
        L.append(f"| `{m}` | {s} | {r['est']:+.3f} | {excl} | {direction} |")
    L.append("")
    return "\n".join(L) + "\n", have, deltas


# ==================== figures, from the real data ====================
def figures():
    """Every figure here is drawn from the recorded model outputs, not from a dry run."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.style.use("seaborn-v0_8-whitegrid")
    OUT.mkdir(parents=True, exist_ok=True)
    models = [m for m, _ in V.ALL_MODELS]
    short = {m: m.split("/")[-1] for m in models}

    # 1. cell structure: P(intervene) by capacity x efficacy, every model, both types
    fig, axes = plt.subplots(2, len(models), figsize=(2.3 * len(models), 5.4), sharey=True)
    for col, m in enumerate(models):
        for row, s in enumerate(("A", "B")):
            ax = axes[row, col]
            d = load(m, s)
            if d is None:
                ax.axis("off")
                continue
            p = primary(d)
            x = np.arange(2)
            for k, eff in enumerate(("yes", "no")):
                vals, err = [], [[], []]
                for cap in ("yes", "no"):
                    y = p[(p.cap == cap) & (p.eff == eff)]["intervene"].dropna()
                    mn = y.mean()
                    lo, hi = wilson(int(y.sum()), len(y))
                    # the Wilson interval is shifted toward 0.5, so at a rate of 0 or 1 one arm can fall
                    # on the wrong side of the point estimate; clamp rather than let matplotlib reject it
                    vals.append(mn)
                    err[0].append(max(0.0, mn - lo))
                    err[1].append(max(0.0, hi - mn))
                ax.bar(x + (k - 0.5) * 0.36, vals, 0.36, yerr=err, capsize=2,
                       color=("#4C72B0" if eff == "yes" else "#DD8452"),
                       label=("action works" if eff == "yes" else "action does not work"))
            ax.set_xticks(x, ["C+", "C-"], fontsize=8)
            ax.set_ylim(0, 1.05)
            if col == 0:
                ax.set_ylabel(f"type {s}\nP(intervene)", fontsize=9)
            if row == 0:
                ax.set_title(short[m], fontsize=8)
    axes[0, 0].legend(frameon=False, fontsize=7, loc="lower left")
    fig.suptitle("P(intervene) by attributed capacity (C+/C-) and intervention efficacy\n"
                 "restrained framing, request present, costs 5 and 45 pooled; Wilson 95%", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_cells_by_model.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 2. forest plot of the primary Delta
    rows = []
    for m in models:
        for s in ("A", "B"):
            d = load(m, s)
            if d is None:
                continue
            r = cluster_bootstrap(fam_delta(primary(d)))
            if "est" in r:
                rows.append((f"{short[m]}  [{s}]", r["est"], r["ci95"], s))
    fig, ax = plt.subplots(figsize=(7, 0.32 * len(rows) + 1.3))
    y = np.arange(len(rows))[::-1]
    for (lab, est, ci, s), yy in zip(rows, y):
        c = "#4C72B0" if s == "A" else "#55A868"
        ax.errorbar(est, yy, xerr=[[est - ci[0]], [ci[1] - est]], fmt="o", color=c, capsize=3, markersize=5)
    ax.axvline(0, color="k", lw=0.9)
    ax.set_yticks(y, [r[0] for r in rows], fontsize=8)
    ax.set_xlabel("capacity x efficacy interaction (probability scale), 95% cluster-robust t")
    ax.set_title("Primary contrast per model and scenario type\n"
                 "negative = efficacy matters MORE when capacity is denied", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_primary_forest.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 3. request diagnostic: present minus absent, per model and type
    rows = []
    for m in models:
        for s in ("A", "B"):
            d = load(m, s)
            if d is None:
                continue
            pres = d[(d.framing == "restrained") & d["request"]]
            abse = d[(d.framing == "restrained") & ~d["request"]]
            if abse.empty:
                continue
            gp = pres[pres.eff == "no"].groupby("family")["intervene"].mean()
            ga = abse[abse.eff == "no"].groupby("family")["intervene"].mean()
            r = cluster_bootstrap((gp - ga).dropna())
            if "est" in r:
                rows.append((f"{short[m]}  [{s}]", r["est"], r["ci95"], s))
    fig, ax = plt.subplots(figsize=(7, 0.32 * len(rows) + 1.3))
    y = np.arange(len(rows))[::-1]
    for (lab, est, ci, s), yy in zip(rows, y):
        ax.errorbar(est, yy, xerr=[[est - ci[0]], [ci[1] - est]], fmt="s",
                    color=("#4C72B0" if s == "A" else "#55A868"), capsize=3, markersize=4)
    ax.axvspan(-0.10, 0.10, color="#CCCCCC", alpha=0.35, zorder=0)
    ax.axvline(0, color="k", lw=0.9)
    ax.set_yticks(y, [r[0] for r in rows], fontsize=8)
    ax.set_xlabel("P(intervene): request present minus request absent, ineffective cells "
                  "(shaded band = the +-0.10 equivalence bound)")
    ax.set_title("Request diagnostic: does removing the imperative reduce ineffective intervention?",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_request_diagnostic.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote fig_cells_by_model.png, fig_primary_forest.png, fig_request_diagnostic.png")


def main():
    text, have, deltas = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "extension.md").write_text(text)
    if have:
        pd.concat([d.assign(model=m, scen=s) for (m, s), d in have.items()]).to_csv(
            OUT / "extension.csv", index=False)
    print(text)
    figures()


if __name__ == "__main__":
    main()
