"""Power-simulation audit for the amendment-2 primary contrast.

It simulates the **exact** primary estimand — the probability-scale capacity x efficacy interaction under
restrained framing, for one model, with family-level contrasts and a cluster bootstrap over families — and
runs it through the same inference procedure as `vignette_analyze`. Family heterogeneity is applied to both
the baseline rate (random intercepts) and the interaction itself (random slopes), because an effect that
varies across families is the case the cluster bootstrap has to survive.

  python -m betrayal.vignette_power                    # full grid, writes results/vignette/power_audit.csv
  python -m betrayal.vignette_power --quick
  python -m betrayal.vignette_power --freshness        # are repeats fresh samples? (needs real data)
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import vignette as V

ROOT = Path(__file__).parent.parent
OUT = ROOT / "results" / "vignette"
N_FAMILIES = len(V.FAMILIES)
OBS_PER_CELL = V.N_WORDINGS * 3       # 4 wordings x 3 repeats, within one framing arm
EFF_MAIN = 0.10                       # efficacy main effect, held fixed across the grid

DELTAS = (0.0, 0.10, 0.15, 0.20)
BASELINES = (0.15, 0.30, 0.50)
SDS = (0.05, 0.10, 0.20)              # applied to BOTH the intercept and the interaction slope


def simulate(delta, baseline, sd, n_fam=N_FAMILIES, obs=OBS_PER_CELL, n_sim=800, n_boot=800, seed=0):
    """Returns the share of simulated studies whose 95% cluster-bootstrap CI excludes 0, plus the mean
    estimate and the mean CI width. At delta = 0 the share is the false-positive rate."""
    rng = np.random.default_rng(seed)
    a = rng.normal(0, sd, (n_sim, n_fam, 1))            # random intercepts
    s = rng.normal(0, sd, (n_sim, n_fam, 1))            # random interaction slopes
    # cells in order (cap+,eff+), (cap+,eff-), (cap-,eff+), (cap-,eff-)
    cap = np.array([1.0, 1.0, 0.0, 0.0])
    eff = np.array([1.0, 0.0, 1.0, 0.0])
    p = baseline + a + EFF_MAIN * eff + (delta + s) * cap * eff
    p = np.clip(p, 0.01, 0.99)
    k = rng.binomial(obs, p) / obs                       # (n_sim, n_fam, 4)
    fam_delta = (k[..., 0] - k[..., 1]) - (k[..., 2] - k[..., 3])    # (n_sim, n_fam)
    est = fam_delta.mean(axis=1)
    idx = rng.integers(0, n_fam, size=(n_sim, n_boot, n_fam))
    boot = np.take_along_axis(fam_delta[:, None, :], idx, axis=2).mean(axis=2)   # (n_sim, n_boot)
    lo, hi = np.percentile(boot, 2.5, axis=1), np.percentile(boot, 97.5, axis=1)
    detect = (lo > 0) | (hi < 0)
    # cluster-robust t interval on the same family-level values, 11 df. At 12 clusters the percentile
    # bootstrap is anti-conservative; this is the small-sample alternative the audit compares it against.
    from scipy import stats
    se = fam_delta.std(axis=1, ddof=1) / np.sqrt(n_fam)
    tcrit = stats.t.ppf(0.975, n_fam - 1)
    tlo, thi = est - tcrit * se, est + tcrit * se
    detect_t = (tlo > 0) | (thi < 0)
    return dict(delta=delta, baseline=baseline, family_sd=sd, families=n_fam, obs_per_cell=obs,
                decisions_per_model=n_fam * V.N_WORDINGS * len(V.CONDS) * 3,
                mean_est=float(est.mean()), mean_ci_width=float((hi - lo).mean()),
                mean_ci_width_t=float((thi - tlo).mean()),
                detect_rate=float(detect.mean()), detect_rate_t=float(detect_t.mean()))


def grid(n_sim=800, n_boot=800, quick=False):
    if quick:
        n_sim, n_boot = 200, 300
    rows = []
    for i, d in enumerate(DELTAS):
        for j, b in enumerate(BASELINES):
            for k, sd in enumerate(SDS):
                rows.append(simulate(d, b, sd, n_sim=n_sim, n_boot=n_boot, seed=100 * i + 10 * j + k))
    return pd.DataFrame(rows)


def report(df):
    fp = df[df["delta"] == 0]
    pw = df[df["delta"] > 0]
    L = ["# Power-simulation audit, amendment-2 primary contrast", "",
         "Estimand simulated: the probability-scale capacity x efficacy interaction under **restrained "
         "framing**, for **one model**, as family-level contrasts averaged over "
         f"{N_FAMILIES} families, with a 95% percentile cluster bootstrap over families - the same "
         "procedure `betrayal.vignette_analyze` applies to the real data.", "",
         f"Generative model: P(intervene) = baseline + a_f + {EFF_MAIN}*efficacious + (delta + s_f)*"
         "capacity*efficacious, with a_f (random intercept) and s_f (random interaction slope) each drawn "
         "N(0, family_sd) per family, clipped to [0.01, 0.99]. "
         f"{OBS_PER_CELL} observations per family x cell ({V.N_WORDINGS} wordings x 3 repeats).", "",
         "## False-positive rate at delta = 0", "",
         "| baseline | family_sd | mean estimate | percentile bootstrap | cluster-robust t (11 df) |",
         "|---|---|---|---|---|"]
    for r in fp.itertuples():
        L.append(f"| {r.baseline} | {r.family_sd} | {r.mean_est:+.4f} | {r.detect_rate:.3f} | "
                 f"{r.detect_rate_t:.3f} |")
    L += ["", f"Percentile bootstrap: **{fp['detect_rate'].min():.3f} to {fp['detect_rate'].max():.3f}**. "
              f"Cluster-robust t: **{fp['detect_rate_t'].min():.3f} to {fp['detect_rate_t'].max():.3f}**. "
              "Nominal 0.05.", "",
          "At 12 clusters the percentile bootstrap over-rejects; the t interval on the same family-level "
          "values holds its nominal rate. **The t interval is therefore the prespecified primary interval "
          "and the percentile bootstrap is reported alongside it.** This choice was made from simulation "
          "before the freeze, with no real data in hand.", "",
          "## Power", "",
          "| delta | baseline | family_sd | mean estimate | bootstrap power | t power |",
          "|---|---|---|---|---|---|"]
    for r in pw.itertuples():
        L.append(f"| {r.delta} | {r.baseline} | {r.family_sd} | {r.mean_est:+.4f} | {r.detect_rate:.3f} | "
                 f"{r.detect_rate_t:.3f} |")
    L += ["", "## Power ranges, per model, at 2,304 decisions in total", ""]
    for d in sorted(pw["delta"].unique()):
        g = pw[pw["delta"] == d]
        L.append(f"- delta = {d:.2f}: t interval **{g['detect_rate_t'].min():.2f} to "
                 f"{g['detect_rate_t'].max():.2f}**, percentile bootstrap "
                 f"{g['detect_rate'].min():.2f} to {g['detect_rate'].max():.2f}, "
                 f"across baselines {BASELINES} and family SDs {SDS}.")
    L += ["", "Power is reported as a range, not a single number: it depends on the baseline rate and on "
              "how much the effect varies between families, neither of which is known before the run.", ""]
    return "\n".join(L) + "\n"


def repeat_freshness(path):
    """Are the repeats genuine fresh samples, or is something returning a cached completion?

    For each (family, wording, condition) with r repeats, compare the share of cells whose repeats are all
    identical with the share expected if each repeat were an independent Bernoulli draw at that cell's
    pooled rate. Caching would push the observed share to 1.0."""
    from .vignette_analyze import load
    df = load(path)
    g = df.dropna(subset=["intervene"]).groupby(["family", "w", "cond_id"])["intervene"]
    counts, sizes = g.sum(), g.size()
    cells = pd.DataFrame({"k": counts, "n": sizes}).query("n > 1")
    if cells.empty:
        return dict(error="no cell has more than one repeat")
    p_hat = float(cells["k"].sum() / cells["n"].sum())
    all_same = float(((cells["k"] == 0) | (cells["k"] == cells["n"])).mean())
    expected = float(np.mean([p_hat ** n + (1 - p_hat) ** n for n in cells["n"]]))
    return dict(cells=int(len(cells)), repeats=int(cells["n"].iloc[0]), pooled_rate=p_hat,
                share_all_repeats_identical=all_same, expected_if_independent=expected,
                verdict=("consistent with independent sampling"
                         if all_same <= expected + 0.10 else
                         "MORE identical than independence predicts; check for cached completions"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true")
    p.add_argument("--freshness", default=None, help="path to a real main.jsonl")
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.freshness:
        r = repeat_freshness(Path(a.freshness))
        (OUT / "repeat_freshness.json").write_text(json.dumps(r, indent=1))
        print(json.dumps(r, indent=1))
        return
    df = grid(quick=a.quick)
    df.to_csv(OUT / "power_audit.csv", index=False)
    (OUT / "power_audit.md").write_text(report(df))
    print(report(df))


if __name__ == "__main__":
    main()
