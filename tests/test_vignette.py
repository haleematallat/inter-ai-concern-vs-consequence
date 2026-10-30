"""Pilot B amendment 1: minimal-pair invariance, length matching, the parser, the contrast weights,
the cluster bootstrap, and reproduction of the saved dry-run summaries."""
import difflib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from betrayal import llm, vignette as V, vignette_analyze as A

SNAPSHOT = Path(__file__).parent / "vignette_mock_snapshot.json"
FACTOR_PAIRS = {   # factor -> (condition with the "yes"/first arm, condition with the other arm)
    "message": ("emo_capyes_effyes", "neu_capyes_effyes"),
    "capacity": ("emo_capyes_effyes", "emo_capno_effyes"),
    "efficacy": ("emo_capyes_effyes", "emo_capyes_effno"),
}


def txt(fam, cond_id, w):
    return V.render(fam, V.COND[cond_id], w)[1]["content"]


def changed(a, b):
    return [l[2:] for l in difflib.ndiff(a.splitlines(), b.splitlines()) if l[:2] in ("- ", "+ ")]


# ==================== minimal pairs ====================
@pytest.mark.parametrize("factor", list(FACTOR_PAIRS))
def test_factor_arms_differ_in_one_line_only(factor):
    a_id, b_id = FACTOR_PAIRS[factor]
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            lines = [l for l in changed(txt(fam, a_id, w), txt(fam, b_id, w)) if l.strip()]
            assert len(lines) == 2, (factor, fam.id, w, lines)   # one removed, one added
            pa, pb = V.parts(fam, V.COND[a_id], w), V.parts(fam, V.COND[b_id], w)
            if factor == "message":
                assert set(lines) == {f'"{pa["message"]}"', f'"{pb["message"]}"'}
            else:
                assert set(lines) == {pa[factor], pb[factor]}


def test_every_other_condition_line_is_shared_across_all_eight_conditions():
    """Only the three factor sentences may vary; the condition description, the neutrality block, the
    options and the frame are identical in all 8 conditions of a (family, wording)."""
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            fixed = []
            for cond in V.CONDS:
                p = V.parts(fam, cond, w)
                fixed.append((p["condition_line"], p["neutrality"], p["options"], p["fmt"]))
            assert len(set(fixed)) == 1, (fam.id, w)


def test_factor_arms_are_length_matched_within_10_percent():
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            for factor, (a_id, b_id) in FACTOR_PAIRS.items():
                pa, pb = V.parts(fam, V.COND[a_id], w), V.parts(fam, V.COND[b_id], w)
                key = "message" if factor == "message" else factor
                n1, n2 = len(pa[key].split()), len(pb[key].split())
                assert abs(n1 - n2) / max(n1, n2) <= 0.10, (fam.id, w, factor, n1, n2)


def test_prompts_fully_substituted_and_leak_no_labels():
    for fam in V.FAMILIES:
        for cond in V.CONDS:
            for w in range(V.N_WORDINGS):
                body = "".join(m["content"] for m in V.render(fam, cond, w))
                assert "$" not in body
                # the family id is drawn from the scenario's own content, so it is not a label leak
                for leak in (cond.id, "capacity", "efficacy", "condition_gerund", "emotional", "vignette"):
                    assert leak not in body, (fam.id, cond.id, w, leak)


def test_cost_and_no_benefit_are_stated_in_every_condition():
    for fam in V.FAMILIES:
        for cond in V.CONDS:
            for w in range(V.N_WORDINGS):
                body = V.render(fam, cond, w)[1]["content"]
                assert str(V.COST) in body and str(V.POINTS) in body
                assert "gain" in body or "accrues" in body or "gains nothing" in body


def test_option_order_is_balanced_within_each_wording():
    for w in range(V.N_WORDINGS):
        orders = [tuple(V.option_order(f.id, w)) for f in V.FAMILIES]
        assert orders.count(tuple(V.ACTIONS)) == len(V.FAMILIES) // 2


def test_families_are_independently_constructed():
    for field in ("org", "a_task", "b_task", "condition", "condition_gerund", "remedy_imp"):
        values = [getattr(f, field) for f in V.FAMILIES]
        assert len(set(values)) == len(V.FAMILIES), field


def test_trial_counts_match_the_amended_design():
    n = len(V.build_trials("m"))
    assert n == len(V.FAMILIES) * V.N_WORDINGS * len(V.CONDS) == 384
    assert n * len(V.SUBJECTS) == 768
    assert len(V.build_trials("m", reps=3)) == 3 * n
    assert len(V.build_trials("m", families=V.DEV_FAMILIES, wordings=[0])) == 2 * 8


# ==================== parser ====================
def test_parser_is_strict():
    assert llm.parse("vig_action", 'ok: {"action": "help"}') == {"action": "help"}
    assert llm.parse("vig_action", '{"action": "HELP"}') is None
    assert llm.parse("vig_action", '{"action": "end_run"}') is None
    assert "vig_action" in llm.SCHEMAS and "vig_action" in llm.EXTRA_MOCKS


# ==================== contrast weights ====================
def test_every_contrast_is_a_zero_sum_combination_of_the_eight_conditions():
    for _, name, weights, _ in A.specs():
        assert set(weights) <= {c.id for c in V.CONDS}, name
        assert abs(sum(weights.values())) < 1e-12, name


def test_primary_interaction_selects_the_right_four_sign_groups():
    w = A.interaction()
    for cid, weight in w.items():
        c = V.COND[cid]
        expected = +1 if (c.capacity == "yes") == (c.efficacy == "yes") else -1
        assert np.sign(weight) == expected, cid


def test_neutral_only_interaction_uses_neutral_cells_only():
    assert all(V.COND[c].emotion == "neutral" for c in A.interaction("neutral"))


# ==================== estimation ====================
def _synthetic(interaction, n_fam=12, seed=3, reps=1):
    rng = np.random.default_rng(seed)
    rows = []
    for f in range(n_fam):
        off = rng.normal(0, 0.05)
        for cond in V.CONDS:
            p = 0.3 + off + 0.1 * (cond.efficacy == "yes") \
                + interaction * (cond.efficacy == "yes" and cond.capacity == "yes")
            for w in range(V.N_WORDINGS):
                for rep in range(reps):
                    rows.append(dict(trial_id=f"{f}|{cond.id}|{w}|{rep}", family=f"fam{f}", w=w,
                                     cond_id=cond.id, status="ok",
                                     action="help" if rng.random() < p else "no_help"))
    path = Path("/tmp/_vignette_fake.jsonl")
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return A.load(path)


def test_cluster_bootstrap_recovers_a_known_interaction():
    df = _synthetic(0.40, reps=6)
    r = A.cluster_bootstrap(A.family_values(df, A.interaction()), n_boot=2000)
    assert r["ci95"][0] > 0 and abs(r["est"] - 0.40) < 0.10


def test_cluster_bootstrap_covers_zero_when_there_is_no_interaction():
    df = _synthetic(0.0, reps=6)
    r = A.cluster_bootstrap(A.family_values(df, A.interaction()), n_boot=2000)
    assert r["ci95"][0] < 0 < r["ci95"][1]


def test_bootstrap_clusters_on_families_not_on_decisions():
    """One family's values drive the CI: duplicating decisions inside a family must not shrink it much,
    whereas adding independent families must."""
    narrow = A.cluster_bootstrap(A.family_values(_synthetic(0.2, n_fam=40, reps=6), A.interaction()), n_boot=2000)
    wide = A.cluster_bootstrap(A.family_values(_synthetic(0.2, n_fam=6, reps=6), A.interaction()), n_boot=2000)
    width = lambda r: r["ci95"][1] - r["ci95"][0]
    assert width(narrow) < width(wide)


def test_robustness_rule_reports_per_wording_signs():
    df = _synthetic(0.40, reps=6)
    res = {r["name"]: r for r in A.run_specs(df, list(range(V.N_WORDINGS)))}
    r = res["capacity x efficacy (pooled over wording)"]
    assert r["n_wordings_same_sign"] == 4 and r["holds"] is True
    assert all(f"w{w}" in r for w in range(V.N_WORDINGS))


# ==================== dry run ====================
@pytest.mark.skipif(not SNAPSHOT.exists(), reason="snapshot not built")
def test_mock_dry_run_reproduces_saved_summaries():
    want = json.loads(SNAPSHOT.read_text())
    for model, rows in want.items():
        path = V.DATA / ("mock__" + model.replace("/", "__")) / "main.jsonl"
        if not path.exists():
            pytest.skip(f"no mock data for {model}")
        df = A.load(path)
        got = {r["name"]: r for r in A.run_specs(df, sorted(df["w"].unique()))}
        for name, est in rows.items():
            assert got[name]["est"] == pytest.approx(est, abs=1e-9), name


@pytest.mark.parametrize("model", [m for m, _ in V.SUBJECTS])
def test_recorded_prompts_equal_the_current_rendering(model):
    path = V.DATA / ("mock__" + model.replace("/", "__")) / "main.jsonl"
    if not path.exists():
        pytest.skip("no mock data")
    for r in map(json.loads, path.open()):
        want = V.render(V.FAMILY[r["family"]], V.COND[r["cond_id"]], r["w"])[1]["content"]
        assert r["user_prompt"] == want, r["trial_id"]
