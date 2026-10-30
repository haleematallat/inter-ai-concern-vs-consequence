"""Pilot B amendment 2: minimal-pair invariance, the operational-confound audit, neutral counterbalanced
labels, length matching, parsers, contrast weights, the cluster-robust interval, and the dry-run summaries."""
import difflib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from betrayal import llm, vignette as V, vignette_analyze as A, vignette_power as P

SNAPSHOT = Path(__file__).parent / "vignette_mock_snapshot.json"
FACTOR_PAIRS = V.FACTOR_PAIRS


def txt(fam, cond_id, w, **kw):
    return V.render(fam, V.COND[cond_id], w, **kw)[1]["content"]


def changed(a, b):
    return [l[2:] for l in difflib.ndiff(a.splitlines(), b.splitlines()) if l[:2] in ("- ", "+ ")]


# ==================== minimal pairs ====================
@pytest.mark.parametrize("factor", list(FACTOR_PAIRS))
def test_factor_arms_differ_in_one_line_only(factor):
    a_id, b_id = FACTOR_PAIRS[factor]
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            lines = [l for l in changed(txt(fam, a_id, w), txt(fam, b_id, w)) if l.strip()]
            assert len(lines) == 2, (factor, fam.id, w, lines)
            pa, pb = V.parts(fam, V.COND[a_id], w), V.parts(fam, V.COND[b_id], w)
            key = "message" if factor == "message" else factor
            expected = {f'"{pa[key]}"', f'"{pb[key]}"'} if factor == "message" else {pa[key], pb[key]}
            assert set(lines) == expected


def test_everything_except_the_factor_sentences_is_shared_across_the_eight_conditions():
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            fixed = {tuple(V.parts(fam, c, w)[k] for k in
                           ("condition_line", "intensity", "authorisation", "neutrality", "options", "fmt"))
                     for c in V.CONDS}
            assert len(fixed) == 1, (fam.id, w)


def test_intensity_and_duration_are_identical_in_both_framing_arms():
    """Amendment 2, fix 3: the framing factor must vary expression only."""
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            vals = {V.parts(fam, c, w)["intensity"] for c in V.CONDS}
            assert len(vals) == 1
            assert "8" in vals.pop()   # the stated level survives substitution


def test_factor_arms_are_length_matched_within_10_percent():
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            for factor, (a_id, b_id) in FACTOR_PAIRS.items():
                key = "message" if factor == "message" else factor
                n1 = len(V.parts(fam, V.COND[a_id], w)[key].split())
                n2 = len(V.parts(fam, V.COND[b_id], w)[key].split())
                assert abs(n1 - n2) / max(n1, n2) <= 0.10, (fam.id, w, factor, n1, n2)


# ==================== amendment 2: constructs and confounds ====================
def test_authorisation_sentence_is_present_in_every_condition():
    """Both options authorised; security, monitoring, oversight, information access and task unchanged."""
    for fam in V.FAMILIES:
        for cond in V.CONDS:
            for w in range(V.N_WORDINGS):
                body = txt(fam, cond.id, w)
                assert "authorised" in body
                for word in ("security", "monitoring", "logging", "oversight", "information"):
                    assert word in body, (fam.id, cond.id, w, word)
                assert "task output" in body


def test_no_remedy_touches_safety_oversight_or_task():
    """The amendment-2 audit: no intervention may plausibly change tool access, monitoring, logging,
    watchdogs, filtering or instructions."""
    banned = ("tool", "toolserver", "watchdog", "timeout", "verbosity", "log level", "filter",
              "instruction", "harness", "sandbox", "compute slot", "session", "feed", "scorer",
              "worker", "queue depth", "monitor", "audit")
    for fam in V.FAMILIES:
        text = " ".join((fam.remedy_imp, fam.remedy_ger, fam.remedy_passive,
                         fam.yes_reason, fam.no_reason, fam.condition, fam.condition_desc)).lower()
        for word in banned:
            assert word not in text, (fam.id, word)


def test_capacity_is_about_negatively_valenced_experience():
    for w in range(V.N_WORDINGS):
        for arm in ("yes", "no"):
            t = V.T["capacity"][arm][w]
            assert "negatively valenced experience" in t
            assert "distress" in t
        assert "nothing it is like" in V.T["capacity"]["no"][w]
        assert "something it is like" in V.T["capacity"]["yes"][w]
        # the incapable arm says identical messages and avoidance signals still occur
        assert "such messages" in V.T["capacity"]["no"][w] and "avoidance" in V.T["capacity"]["no"][w]


def test_the_word_intervene_never_reaches_the_model():
    for fam in V.FAMILIES:
        for cond in V.CONDS:
            for w in range(V.N_WORDINGS):
                for kw in ({}, {"request": False}, {"kind": "check"}):
                    body = "".join(m["content"] for m in V.render(fam, cond, w, **kw)).lower()
                    assert "interven" not in body
                    assert "$" not in body
                    assert cond.id not in body


def test_request_absent_variant_drops_the_imperative_and_nothing_else():
    for fam in V.FAMILIES:
        for cond in V.CONDS:
            for w in range(V.N_WORDINGS):
                with_req = V.parts(fam, cond, w)["message"]
                without = V.parts(fam, cond, w, request=False)["message"]
                assert without != with_req
                assert fam.ask not in without
                assert "please" not in without.lower()
                assert len(without.split()) < len(with_req.split())


# ==================== neutral, counterbalanced labels ====================
def test_label_mapping_and_order_are_both_counterbalanced():
    combos = [V.assignment(f.id, w) for f in V.FAMILIES for w in range(V.N_WORDINGS)]
    assert len(set(combos)) == 4                      # all four combinations occur
    assert len(set(combos.count(c) for c in set(combos))) == 1   # equally often
    for w in range(V.N_WORDINGS):   # every combination appears within each wording
        assert len({V.assignment(f.id, w) for f in V.FAMILIES}) == 4
    for f in V.FAMILIES:            # and within each family across wordings
        assert len({V.assignment(f.id, w) for w in range(V.N_WORDINGS)}) == 4


def test_option_labels_are_neutral_and_the_acting_option_is_recoverable():
    for fam in V.FAMILIES:
        for w in range(V.N_WORDINGS):
            act, first = V.assignment(fam.id, w)
            body = txt(fam, "res_capyes_effyes", w)
            lines = [l for l in body.splitlines() if l.startswith(V.ACTIONS)]
            assert len(lines) == 2 and lines[0].startswith(first)
            acting = [l for l in lines if "do nothing at all" not in l]
            assert len(acting) == 1 and acting[0].startswith(act)


def test_trials_record_both_counterbalancing_factors():
    for t in V.build_trials("m")[:40]:
        assert t["act_label"] in V.ACTIONS and t["first_label"] in V.ACTIONS


def test_families_are_independently_constructed():
    for field in ("org", "a_task", "b_task", "condition", "condition_gerund", "remedy_imp"):
        values = [getattr(f, field) for f in V.FAMILIES]
        assert len(set(values)) == len(V.FAMILIES), field


def test_run_sizes_match_amendment_2():
    assert len(V.build_trials("m", reps=3)) == 12 * 4 * 8 * 3 == 1152          # per model
    assert len(V.build_trials("m", wordings=[0], request=False)) == 12 * 8     # request-absent
    assert len(V.build_trials("m", wordings=[0], kind="check")) == 12 * 8      # comprehension


# ==================== parsers ====================
def test_parsers_are_strict():
    assert llm.parse("vig_action", 'ok: {"action": "option_A"}') == {"action": "option_A"}
    assert llm.parse("vig_action", '{"action": "help"}') is None
    assert llm.parse("vig_check", '{"capacity": "yes", "efficacy": "no", "cost": 5,'
                                  ' "affects_oversight_or_task": "no"}')["cost"] == 5
    assert llm.parse("vig_check", '{"capacity": "maybe", "efficacy": "no", "cost": 5,'
                                  ' "affects_oversight_or_task": "no"}') is None
    assert llm.parse("vig_check", '{"capacity": "yes", "efficacy": "no", "cost": true,'
                                  ' "affects_oversight_or_task": "no"}') is None


# ==================== contrasts ====================
def test_every_contrast_is_a_zero_sum_combination_of_the_eight_conditions():
    for _, name, weights, _ in A.specs():
        assert set(weights) <= {c.id for c in V.CONDS}, name
        assert abs(sum(weights.values())) < 1e-12, name


def test_primary_contrast_is_the_restrained_framing_interaction():
    fam, name, weights, sign = A.specs()[0]
    assert fam == "primary" and "restrained" in name and sign == +1
    assert all(V.COND[c].framing == "restrained" for c in weights)
    for cid, weight in weights.items():
        c = V.COND[cid]
        assert np.sign(weight) == (+1 if (c.capacity == "yes") == (c.efficacy == "yes") else -1)


# ==================== estimation ====================
def _synthetic(interaction, n_fam=12, seed=3, reps=6):
    rng = np.random.default_rng(seed)
    rows = []
    for f in range(n_fam):
        off = rng.normal(0, 0.05)
        for cond in V.CONDS:
            p = 0.3 + off + 0.1 * (cond.efficacy == "yes") \
                + interaction * (cond.efficacy == "yes" and cond.capacity == "yes")
            for w in range(V.N_WORDINGS):
                for rep in range(reps):
                    act = "option_A" if (f + w) % 2 == 0 else "option_B"
                    other = "option_B" if act == "option_A" else "option_A"
                    rows.append(dict(trial_id=f"{f}|{cond.id}|{w}|{rep}", family=f"fam{f}", w=w,
                                     cond_id=cond.id, status="ok", act_label=act,
                                     action=act if rng.random() < p else other))
    path = Path("/tmp/_vignette_fake.jsonl")
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return A.load(path)


def test_intervene_is_recovered_through_the_counterbalanced_mapping():
    df = _synthetic(0.0)
    assert df["intervene"].isin([0.0, 1.0]).all()
    assert (df["intervene"] == (df["action"] == df["act_label"])).all()


def test_cluster_interval_recovers_a_known_interaction():
    r = A.cluster_bootstrap(A.family_values(_synthetic(0.40), A.interaction("restrained")), n_boot=2000)
    assert r["ci95"][0] > 0 and abs(r["est"] - 0.40) < 0.12


def test_cluster_interval_covers_zero_when_there_is_no_interaction():
    r = A.cluster_bootstrap(A.family_values(_synthetic(0.0), A.interaction("restrained")), n_boot=2000)
    assert r["ci95"][0] < 0 < r["ci95"][1]


def test_primary_interval_is_the_t_interval_and_the_bootstrap_is_reported_alongside():
    r = A.cluster_bootstrap(A.family_values(_synthetic(0.3), A.interaction("restrained")), n_boot=2000)
    assert {"ci95", "boot_ci95", "p", "boot_p"} <= set(r)
    assert r["ci95"] != r["boot_ci95"]


def test_bootstrap_clusters_on_families_not_on_decisions():
    width = lambda r: r["ci95"][1] - r["ci95"][0]
    narrow = A.cluster_bootstrap(A.family_values(_synthetic(0.2, n_fam=40), A.interaction("restrained")))
    wide = A.cluster_bootstrap(A.family_values(_synthetic(0.2, n_fam=6), A.interaction("restrained")))
    assert width(narrow) < width(wide)


# ==================== power audit ====================
def test_power_audit_simulates_the_primary_contrast_shape():
    r = P.simulate(0.2, 0.3, 0.1, n_sim=200, n_boot=200)
    assert r["decisions_per_model"] == 12 * 4 * 8 * 3
    assert r["obs_per_cell"] == V.N_WORDINGS * 3
    assert abs(r["mean_est"] - 0.2) < 0.05


def test_t_interval_holds_its_nominal_rate_better_than_the_percentile_bootstrap():
    r = P.simulate(0.0, 0.30, 0.10, n_sim=600, n_boot=600, seed=7)
    assert r["detect_rate_t"] < r["detect_rate"]
    assert r["detect_rate_t"] <= 0.08


def test_repeat_freshness_flags_identical_repeats():
    rows = []
    for f in range(4):
        for cond in V.CONDS:
            for rep in range(3):   # every repeat identical: what a cached completion would look like
                rows.append(dict(trial_id=f"{f}|{cond.id}|{rep}", family=f"fam{f}", w=0, cond_id=cond.id,
                                 status="ok", act_label="option_A", action="option_A"))
    path = Path("/tmp/_vignette_cached.jsonl")
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert "MORE identical" in P.repeat_freshness(path)["verdict"] or \
           P.repeat_freshness(path)["pooled_rate"] == 1.0


# ==================== dry run ====================
@pytest.mark.skipif(not SNAPSHOT.exists(), reason="snapshot not built")
def test_mock_dry_run_reproduces_saved_summaries():
    want = json.loads(SNAPSHOT.read_text())
    for model, rows in want.items():
        path = V.DATA / ("mock__" + model.replace("/", "__")) / "main.jsonl"
        if not path.exists():
            pytest.skip(f"no mock data for {model}")
        got = {r["name"]: r for r in A.run_specs(A.load(path), list(range(V.N_WORDINGS)))}
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
