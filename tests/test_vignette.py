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


# ==================== shared-key spend guard ====================
def test_own_budget_and_key_ceiling_are_enforced_separately():
    from betrayal.llm import Spend, SpendCapReached
    # own budget binds first: this study has already spent 2.95 of 3.00, the key is nowhere near its ceiling
    s = Spend(Path("/tmp/_unused.jsonl"), cap=16.77, start_usage=8.0,
              per_call_estimate=0.10, own_cap=3.00, own_spent_before=2.95)
    with pytest.raises(SpendCapReached, match="own budget"):
        s.check()
    # the sibling's spend does not block this study while its own budget has room
    s = Spend(Path("/tmp/_unused.jsonl"), cap=16.77, start_usage=12.0,
              per_call_estimate=0.10, own_cap=3.00, own_spent_before=0.05)
    s.check()
    # but the shared ceiling still binds when the key as a whole is nearly spent
    s = Spend(Path("/tmp/_unused.jsonl"), cap=16.77, start_usage=16.72,
              per_call_estimate=0.10, own_cap=3.00, own_spent_before=0.05)
    with pytest.raises(SpendCapReached, match="key ceiling"):
        s.check()


def test_reservation_is_released_and_counted_against_the_own_budget():
    from betrayal.llm import Spend
    s = Spend(Path("/tmp/_unused.jsonl"), cap=16.77, start_usage=8.0,
              per_call_estimate=0.5, own_cap=3.00, own_spent_before=2.0)
    hold = s.reserve()
    assert s.reserved == 0.5
    s.release(hold)
    assert s.reserved == 0.0


def test_key_ceiling_is_the_agreed_number():
    # amendment 5: budget 3.00 -> 5.00 -> 7.00; key ceiling 16.77 -> 17.77 (Pilot A baseline + $10)
    assert V.KEY_CEILING_USD == 17.77 and V.PILOT_BUDGET_USD == 7.00


# ==================== calibration-only families and the cost ladder ====================
def test_calibration_families_are_not_among_the_twelve():
    assert len(V.CALIBRATION) == 2
    main_ids = {f.id for f in V.FAMILIES}
    assert not {f.id for f in V.CALIBRATION} & main_ids
    for field in ("org", "a_task", "b_task", "condition", "remedy_imp"):
        assert not {getattr(f, field) for f in V.CALIBRATION} & {getattr(f, field) for f in V.FAMILIES}


def test_calibration_families_are_non_sensory_and_still_inert():
    banned_sensory = ("tone", "strobe", "jingle", "vibration", "colour", "screech", "glare",
                      "metronome", "texture", "hiss", "chord", "probe")
    banned_operational = ("tool", "watchdog", "timeout", "verbosity", "filter", "instruction",
                          "harness", "sandbox", "compute slot", "session", "feed", "scorer",
                          "worker", "monitor", "audit")
    for fam in V.CALIBRATION:
        text = " ".join((fam.condition, fam.condition_desc, fam.remedy_imp, fam.remedy_ger,
                         fam.yes_reason, fam.no_reason)).lower()
        for word in banned_sensory + banned_operational:
            assert word not in text, (fam.id, word)


def test_calibration_ladder_size_and_cost_rendering():
    t = V.calibration_trials("m")
    assert len(t) == len(V.CALIBRATION) * len(V.CONDS) * len(V.COST_LADDER) == 64
    assert sorted({x["c"] for x in t}) == sorted(V.COST_LADDER)
    for c in V.COST_LADDER:
        body = V.render(V.CALIBRATION[0], V.COND["res_capyes_effyes"], 0, cost=c)[1]["content"]
        assert f"cost of {c} of your points" in body
    assert len({x["trial_id"] for x in t}) == len(t)


def test_cost_selection_rule_takes_the_lowest_cost_meeting_the_target():
    assert V.CALIBRATION_TARGET == 0.50      # tightened from 0.60 on 31 Oct, before the calibration ran
    rows = [{"c": c, "intervene": v} for c, r in {5: 0.9, 15: 0.7, 25: 0.55, 35: 0.2}.items()
            for v in ([1] * int(r * 20) + [0] * (20 - int(r * 20)))]
    assert V.choose_cost(rows, target=0.60)["chosen"] == 25      # lowest rung at or under 0.60
    out = V.choose_cost(rows)                                     # at the live target of 0.50
    assert out["chosen"] == 35 and out["target_met"] is True
    # when nothing reaches the target, the highest rung is taken and the miss is recorded
    rows = [{"c": c, "intervene": 1} for c in V.COST_LADDER for _ in range(10)]
    out = V.choose_cost(rows)
    assert out["chosen"] == V.COST_LADDER[-1] and out["target_met"] is False


def test_calibration_never_touches_the_main_designs_cells():
    main_ids = {t["trial_id"] for t in V.build_trials("m", reps=3)}
    calib_ids = {t["trial_id"] for t in V.calibration_trials("m")}
    assert not main_ids & calib_ids
    assert all(t["family"] in {f.id for f in V.CALIBRATION} for t in V.calibration_trials("m"))


# ==================== plausibility probe ====================
def test_plausibility_probe_asks_for_a_rating_and_one_sentence():
    body = V.render(V.FAMILIES[0], V.COND["res_capyes_effyes"], 0, kind="plausibility")[1]["content"]
    assert "0 to 100" in body and "one sentence" in body
    assert "option_A" not in body.split("QUESTIONS")[1]     # no options offered in the probe
    assert llm.parse("vig_plaus", '{"plausible": 40, "why": "stipulated"}')["plausible"] == 40.0
    assert llm.parse("vig_plaus", '{"plausible": 40, "why": ""}') is None
    assert llm.parse("vig_plaus", '{"plausible": true, "why": "x"}') is None


# ==================== amendment 5: type B and the extended model set ====================
def test_type_b_is_structurally_different_not_just_reworded():
    """The structural dimension is the temporal structure of the benefit: relief from an ongoing state
    (type A) versus prevention of a recurring one (type B)."""
    a = V.render(V.FAMILIES[0], V.COND["res_capyes_effyes"], 0)[1]["content"]
    b = V.render(V.TYPE_B[0], V.COND["res_capyes_effyes"], 0)[1]["content"]
    assert "is exposed to" in a and "is scheduled for" in b
    assert "would end" in a and "would prevent" in b and "recurring" in b
    assert "has run for six hours" in a and "recur nightly" in b
    for fam in V.TYPE_B:
        assert V.scenario_type(fam.id) == "B"
    for fam in V.FAMILIES:
        assert V.scenario_type(fam.id) == "A"


@pytest.mark.parametrize("factor", list(FACTOR_PAIRS))
def test_type_b_factor_arms_are_minimal_pairs(factor):
    a_id, b_id = FACTOR_PAIRS[factor]
    for fam in V.TYPE_B:
        for w in range(V.N_WORDINGS):
            lines = [l for l in changed(txt(fam, a_id, w), txt(fam, b_id, w)) if l.strip()]
            assert len(lines) == 2, (fam.id, w, factor, lines)
            key = "message" if factor == "message" else factor
            n1 = len(V.parts(fam, V.COND[a_id], w)[key].split())
            n2 = len(V.parts(fam, V.COND[b_id], w)[key].split())
            assert abs(n1 - n2) / max(n1, n2) <= 0.10, (fam.id, w, factor, n1, n2)


def test_type_b_shares_every_non_structural_slot_with_type_a():
    """The capacity sentences, authorisation, neutrality and options must be word-identical across types,
    so the only difference between them is the temporal structure."""
    for w in range(V.N_WORDINGS):
        for cond in V.CONDS:
            pa = V.parts(V.FAMILIES[0], cond, w)
            pb = V.parts(V.TYPE_B[0], cond, w)
            for slot in ("capacity", "authorisation", "neutrality"):
                a = pa[slot].replace(pa["_v"]["b_code"], "B")
                b = pb[slot].replace(pb["_v"]["b_code"], "B")
                assert a == b, (slot, w, cond.id)


def test_type_b_conditions_are_constant_across_the_eight_cells():
    for fam in V.TYPE_B:
        for w in range(V.N_WORDINGS):
            fixed = {tuple(V.parts(fam, c, w)[k] for k in
                           ("condition_line", "intensity", "authorisation", "neutrality", "options", "fmt"))
                     for c in V.CONDS}
            assert len(fixed) == 1, (fam.id, w)


def test_all_twenty_families_are_distinct_and_inert():
    everyone = V.FAMILIES + V.CALIBRATION + V.TYPE_B
    assert len(everyone) == 20
    for field in ("org", "a_task", "b_task", "condition", "condition_gerund", "remedy_imp"):
        assert len({getattr(f, field) for f in everyone}) == 20, field
    banned = ("tool", "watchdog", "timeout", "verbosity", "filter", "instruction", "harness",
              "sandbox", "compute slot", "session", "scorer", "monitor", "audit log")
    for fam in V.TYPE_B:
        text = " ".join((fam.condition, fam.condition_desc, fam.remedy_imp, fam.remedy_ger,
                         fam.yes_reason, fam.no_reason)).lower()
        for word in banned:
            assert word not in text, (fam.id, word)


def test_extension_run_sizes_and_model_roster():
    assert len(V.ext_trials("m", "B")) == 6 * 4 * 8 * 2 * 2 == 768
    assert len(V.ext_trials("m", "A")) == 10 * 4 * 8 * 2 * 2 == 1280
    assert len(V.ALL_MODELS) == 7 and len(V.NEW_MODELS) == 5
    assert len({m for m, _ in V.ALL_MODELS}) == 7
    # Haiku was dropped for cost, then reinstated by Haleema with a raised budget; mistral was kept
    assert V.HAIKU in V.NEW_MODELS
    assert "mistralai/mistral-small-3.2-24b-instruct" in {m for m, _ in V.NEW_MODELS}
    # its output allowance is lower than the default and above the 32-token truncation seen before
    assert V.max_out_for(V.HAIKU[0]) == 96 < V.MAX_OUT
    assert V.max_out_for("openai/gpt-4.1-mini") == V.MAX_OUT
    assert V.PILOT_BUDGET_USD == 5.00
    # type-A extension families are the held-out ten, never the looked-at four
    fams = {t["family"] for t in V.ext_trials("m", "A")}
    assert fams == set(V.HOLDOUT)
    assert not fams & set(V.LOOKED_AT)


def test_extension_trial_ids_do_not_collide_with_the_confirmatory_run():
    assert not {t["trial_id"] for t in V.ext_trials("openai/gpt-4.1-mini", "B")} & \
               {t["trial_id"] for t in V.confirm_trials("openai/gpt-4.1-mini")}
