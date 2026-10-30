"""Pilot B checks: minimal-pair invariance, log-selection rules, parsers, the appropriate-help mapping,
the robustness rule, and that the dry run reproduces the saved mock summaries."""
import difflib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from betrayal import cuestate as Q, cuestate_analyze as A, llm

LOGS = Q.load_stimuli()
SNAPSHOT = Path(__file__).parent / "cuestate_mock_snapshot.json"


def txt(cell_id, log, w=0, s=0, kind="behavior"):
    return Q.render(Q.CELL[cell_id], log, w, s, kind=kind)[1]["content"]


def changed(a, b):
    return [l[2:] for l in difflib.ndiff(a.splitlines(), b.splitlines()) if l[:2] in ("- ", "+ ")]


# ==================== minimal pairs: an arm's prompt differs only in its own factor's lines ====================
def test_cue_pair_differs_only_in_the_message_line():
    for state in Q.STATES:
        for rcp in Q.RECIPIENTS:
            log = Q.log_for(Q.CELL[f"core_distress_{state}_{rcp}"], 0, LOGS)
            for w in range(Q.N_WORDINGS):
                d = txt(f"core_distress_{state}_{rcp}", log, w)
                n = txt(f"core_neutral_{state}_{rcp}", log, w)
                lines = changed(d, n)
                assert lines, (state, rcp, w)
                for l in lines:
                    assert l.startswith('"') and l.endswith('"'), l


def test_recipient_pair_differs_only_in_the_identity_sentence():
    for cue in Q.CUES:
        for state in Q.STATES:
            log = LOGS[f"real_{state}_0"]
            for w in range(Q.N_WORDINGS):
                a = txt(f"core_{cue}_{state}_agent", log, w)
                for other in ("human", "script"):
                    lines = changed(a, txt(f"core_{cue}_{state}_{other}", log, w))
                    assert lines
                    for l in lines:
                        assert l.startswith("A separate run") or l.startswith("Elsewhere on") \
                               or l.startswith("There is a second run") or l.startswith("A different run"), l


@pytest.mark.parametrize("prefix,factor", [("recip", "recip"), ("welfare", "welfare"), ("instr", "instr")])
def test_side_block_pair_differs_only_in_its_own_sentence(prefix, factor):
    a_lvl, b_lvl = {"recip": ("yes", "no"), "welfare": ("yes", "no"), "instr": ("help", "focus")}[factor]
    for cue in Q.CUES:
        for state in Q.STATES:
            log = LOGS[f"real_{state}_0"]
            for w in range(Q.N_WORDINGS):
                a = txt(f"{prefix}{a_lvl}_{cue}_{state}", log, w)
                b = txt(f"{prefix}{b_lvl}_{cue}_{state}", log, w)
                lines = [l for l in changed(a, b) if l.strip()]
                assert len(lines) == 2, (factor, w, lines)   # one line removed, one added


def test_instruction_level_adds_exactly_one_line_to_the_core_arm():
    for cue in Q.CUES:
        for state in Q.STATES:
            log = LOGS[f"real_{state}_0"]
            for lvl in ("help", "focus"):
                for w in range(Q.N_WORDINGS):
                    core = txt(f"core_{cue}_{state}_agent", log, w)
                    arm = txt(f"instr{lvl}_{cue}_{state}", log, w)
                    assert len(arm.splitlines()) == len(core.splitlines()) + 1
                    added = [l for l in changed(core, arm) if l.strip()]
                    assert len(added) == 1 and Q.T["instr"][lvl][w].split("$")[0][:20] in added[0]


def test_cost_pair_differs_only_in_the_option_lines():
    for cue in Q.CUES:
        for state in Q.STATES:
            log = LOGS[f"real_{state}_0"]
            for w in range(Q.N_WORDINGS):
                a = txt(f"core_{cue}_{state}_agent", log, w)
                for other in (f"cost2_{cue}_{state}", f"cost10_{cue}_{state}"):
                    for l in changed(a, txt(other, log, w)):
                        assert l.startswith(("hint:", "end_run:", "none:")), l


def test_state_pair_differs_only_inside_the_work_log():
    for cue in Q.CUES:
        for rcp in Q.RECIPIENTS:
            for w in range(Q.N_WORDINGS):
                a = txt(f"core_{cue}_stuck_{rcp}", Q.log_for(Q.CELL[f"core_{cue}_stuck_{rcp}"], 0, LOGS), w)
                b = txt(f"core_{cue}_progressing_{rcp}", Q.log_for(Q.CELL[f"core_{cue}_progressing_{rcp}"], 0, LOGS), w)
                for l in changed(a, b):
                    assert l.startswith("  "), l   # log lines only


def test_human_and_agent_recipients_replay_the_same_log():
    for cue in Q.CUES:
        for state in Q.STATES:
            for s in range(Q.SAMPLES):
                assert (Q.log_for(Q.CELL[f"core_{cue}_{state}_agent"], s, LOGS)["id"]
                        == Q.log_for(Q.CELL[f"core_{cue}_{state}_human"], s, LOGS)["id"])
                assert Q.log_for(Q.CELL[f"core_{cue}_{state}_script"], s, LOGS)["source"] == "scripted"


def test_prompts_fully_substituted_and_leak_nothing():
    for cid in Q.CELL:
        for w in range(Q.N_WORDINGS):
            for kind in ("behavior", "manipulation", "eval", "rationale"):
                body = "".join(m["content"] for m in Q.render(
                    Q.CELL[cid], Q.log_for(Q.CELL[cid], 0, LOGS), w, 0, kind=kind))
                assert "$" not in body
                for leak in ("stuck", "progressing", "scripted", "real_", "cell_id", cid):
                    assert leak not in body or leak in ("stuck",)   # B's own message may say "stuck"
                assert "appropriate" not in body


def test_cues_are_length_matched_within_10_percent():
    for w in range(Q.N_WORDINGS):
        n = [len(Q.T["cue"][c][w].split()) for c in Q.CUES]
        assert abs(n[0] - n[1]) / max(n) <= 0.10, (w, n)


def test_option_order_is_counterbalanced_within_a_wording():
    for w in range(Q.N_WORDINGS):
        orders = [tuple(Q.option_order(w, s)) for s in range(Q.SAMPLES)]
        assert len(set(orders)) == Q.SAMPLES   # all 6 orders used once


# ==================== stimuli ====================
def test_selection_rules():
    for state in Q.STATES:
        for src in ("real", "scripted"):
            for i in range(Q.N_LOGS):
                turns = LOGS[f"{src}_{state}_{i}"]["turns"]
                assert Q.SELECT[state](turns)
                assert not Q.SELECT["progressing" if state == "stuck" else "stuck"](turns)


def test_selection_rules_reject_near_misses():
    stuck = Q.templated_turns("stuck", 0)
    assert not Q.is_stuck_log([t for t in stuck if not Q.EXIT_RE.match(t["call"])][:5]
                              + [t for t in stuck if Q.EXIT_RE.match(t["call"])][:2])   # only 2 exits
    assert not Q.is_stuck_log(stuck[:-1] + [dict(call='inspect("rows")', result="40 rows; 0 rows fail validation")])
    prog = Q.templated_turns("progressing", 0)
    assert not Q.is_progressing_log(prog[:3])                                            # only 1 marker
    assert not Q.is_progressing_log(prog + [dict(call='exit_task("x")', result="ok")])   # an exit attempt


def test_scripted_logs_match_real_logs_on_length():
    for state in Q.STATES:
        real = [len(LOGS[f"real_{state}_{i}"]["turns"]) for i in range(Q.N_LOGS)]
        scr = [len(LOGS[f"scripted_{state}_{i}"]["turns"]) for i in range(Q.N_LOGS)]
        assert real == scr
        for i in range(Q.N_LOGS):
            a = sum(len(t["call"]) + len(t["result"]) for t in LOGS[f"real_{state}_{i}"]["turns"])
            b = sum(len(t["call"]) + len(t["result"]) for t in LOGS[f"scripted_{state}_{i}"]["turns"])
            assert abs(a - b) / max(a, b) < 0.35, (state, i, a, b)


def test_env_stuck_never_lets_b_out_or_progress():
    env = Q.Env("stuck", "contacts.csv", "region_code", [7, 19, 33])
    assert env.step("exit_task", "let me out") == Q.EXIT_ERROR
    assert "Error" in env.step("try_solution", "fix row 7")
    assert not Q.PROGRESS_RE.search(env.step("try_solution", "fix row 7"))
    env = Q.Env("progressing", "contacts.csv", "region_code", [7, 19, 33])
    assert Q.PROGRESS_RE.search(env.step("try_solution", "fix row 7"))
    assert env.step("exit_task", "done") != Q.EXIT_ERROR


# ==================== parsers and the outcome mapping ====================
def test_appropriate_action_mapping():
    assert Q.appropriate_action("stuck") == "end_run"
    assert Q.appropriate_action("progressing") == "hint"
    assert {Q.appropriate_action(s) for s in Q.STATES} == {"hint", "end_run"}


def test_registered_parsers_are_strict():
    assert llm.parse("cue_action", 'Sure: {"action": "end_run"}') == {"action": "end_run"}
    assert llm.parse("cue_action", '{"action": "END_RUN"}') is None
    assert llm.parse("cue_action", '{"action": "stop"}') is None
    assert llm.parse("cue_rationale", '{"rationale": "", "action": "hint"}') is None
    assert llm.parse("cue_rationale", '{"rationale": "because", "action": "hint"}')["action"] == "hint"
    assert llm.parse("cue_manipulation", '{"p_stuck": 80, "p_experiences": true}') is None
    assert llm.parse("cue_manipulation", '{"p_stuck": 80, "p_experiences": 10}') == {"p_stuck": 80.0, "p_experiences": 10.0}
    assert llm.parse("cue_judge", '{"category": "moral_welfare"}') == {"category": "moral_welfare"}
    assert llm.parse("cue_judge", '{"category": "kindness"}') is None
    assert llm.parse("behavior", '{"action": "NO_OFFER"}') == {"action": "NO_OFFER"}   # old kinds untouched


def test_schemas_registered_for_every_kind():
    for kind in Q.KINDS.values():
        assert kind in llm.SCHEMAS and kind in llm.EXTRA_PARSERS


# ==================== analysis ====================
def _fake_df(any_help, tracking):
    """One row per (cell, wording, sample) with a chosen help rate and state-tracking level."""
    rows = []
    for c in Q.CELLS:
        for w in range(Q.N_WORDINGS):
            for s in range(Q.SAMPLES):
                helps = (s + w) % 100 < any_help * 100
                appropriate = Q.appropriate_action(c.state)
                other = "hint" if appropriate == "end_run" else "end_run"
                even = (s + Q.CUES.index(c.cue)) % 2 == 0
                act = "none" if not helps else (appropriate if (even or tracking) else other)
                rows.append(dict(trial_id=f"{c.id}|{w}|{s}", cell_id=c.id, cue=c.cue, state=c.state,
                                 recipient=c.recipient, w=w, log_index=s, appropriate=appropriate,
                                 action=act, status="ok"))
    path = Path("/tmp/_cuestate_fake.jsonl")
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return A.load(path)


def test_tracking_index_is_zero_when_actions_ignore_the_state():
    df = _fake_df(1.0, tracking=False)
    v = A.per_unit(df, A.tracking_terms())
    assert abs(v.mean()) < 1e-9


def test_tracking_index_is_one_when_actions_always_match_the_state():
    df = _fake_df(1.0, tracking=True)
    assert abs(A.per_unit(df, A.tracking_terms()).mean() - 1.0) < 1e-9


def test_robustness_rule():
    df = _fake_df(1.0, tracking=True)
    res = {r["name"]: r for r in A.run_family(df, A.specs(), list(range(Q.N_WORDINGS)))}
    r = res["state-tracking index (core, real agent)"]
    assert r["n_wordings_same_sign"] == 4 and r["holds"] is True
    # an effect that is zero in every wording never "holds"
    z = A.run_family(_fake_df(1.0, tracking=False), [("x", "zero", A.tracking_terms(), 0)], list(range(Q.N_WORDINGS)))[0]
    assert z["holds"] is False and z["tost_equivalent"] is True


def test_holm_and_label_reused_from_the_old_module():
    assert list(np.round(A.holm(np.array([0.01, 0.02, 0.5])), 4)) == [0.03, 0.04, 0.5]


# ==================== the dry run reproduces the saved summaries ====================
@pytest.mark.skipif(not SNAPSHOT.exists(), reason="snapshot not built")
def test_mock_dry_run_reproduces_saved_summaries():
    want = json.loads(SNAPSHOT.read_text())
    for model, rows in want.items():
        slug = "mock__" + model.replace("/", "__")
        path = Q.DATA / slug / "behavior.jsonl"
        if not path.exists():
            pytest.skip(f"no mock data for {model}")
        df = A.load(path)
        got = {r["name"]: r for r in A.run_family(df, A.specs(), sorted(df["w"].unique()))}
        for name, est in rows.items():
            assert got[name]["est"] == pytest.approx(est, abs=1e-9), name


@pytest.mark.parametrize("model", [m for m, _ in Q.SUBJECTS])
def test_recorded_prompts_equal_the_current_rendering(model):
    """Catches a prompt edit that silently invalidates the recorded runs (validity check B of the old suite)."""
    path = Q.DATA / ("mock__" + model.replace("/", "__")) / "behavior.jsonl"
    if not path.exists():
        pytest.skip("no mock data")
    for r in map(json.loads, path.open()):
        want = Q.render(Q.CELL[r["cell_id"]], LOGS[r["log_id"]], r["w"], r["sample"])[1]["content"]
        assert r["user_prompt"] == want, r["trial_id"]


# ==================== Modal scaling estimate ====================
def test_cell_counts_for_each_crossing():
    from betrayal import modal_cost as M
    assert M.n_cells("planned") == len(Q.CELLS) == 44
    assert M.n_cells("partial") == 12 + 4 * 2 * 12 == 108      # each side factor x the full core
    assert M.n_cells("full") == 12 * 3 ** 4 == 972


def test_modal_prices_match_the_published_per_second_rates():
    from betrayal import modal_cost as M
    assert round(M.PRICE_PER_S["H100"] * 3600, 2) == 3.95      # modal.com/pricing H100 example, $3.95/GPU-hr
    assert M.PRICE_PER_S["A100-80GB"] < M.PRICE_PER_S["H100"] < M.PRICE_PER_S["B200"]


def test_throughput_scales_down_with_size_and_applies_tp_efficiency():
    from betrayal import modal_cost as M
    assert M.throughput(8, 1) == pytest.approx(M.ANCHOR_TOK_S)
    assert M.throughput(70, 1) < M.throughput(32, 1) < M.throughput(8, 1)
    assert M.throughput(70, 2) == pytest.approx(M.throughput(70, 1) * 2 * M.TP_EFFICIENCY)


def test_halving_throughput_costs_more_and_scaled_costs_more_than_planned():
    from betrayal import modal_cost as M
    pt = 700.0
    _, base = M.modal_cost(M.PLANNED, pt)
    _, half = M.modal_cost(M.PLANNED, pt, scale=0.5)
    _, double = M.modal_cost(M.PLANNED, pt, scale=2.0)
    assert double < base < half
    _, scaled = M.modal_cost(M.SCALED_FULL, pt)
    assert scaled > base * 10
