"""Re-test every claim in REPORT.md against the numbers the analysis scripts saved.

Each check reads results/metrics/*.json (written by analysis/0X_*.py) and applies the
condition stated next to it. Output: a PASS/FAIL table on screen and in results/claims_check.txt.
Run after run_all.py (or after the analysis scripts):   python check_claims.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M = {}
for f in sorted((ROOT / "results" / "metrics").glob("*.json")):
    for cid, v in json.loads(f.read_text()).items():
        M[cid] = (f.stem, v)


def g(cid):
    return M[cid][1]


CHECKS = [
    ("C01", "all four areas have exactly 100 cells",
     lambda: all(v == 100 for v in g("C01")["sizes"].values())),
    ("C02", "Areas 1-3 change at most 1 cell per step; Area 4 changes 0 or 2 (all datasets)",
     lambda: all(max(v[a] for a in ("1", "2", "3")) <= 1 for v in g("C02")["max_cells_changed"].values())
     and all(set(v) <= {0, 2} for v in g("C02")["area4_counts_seen"].values())),
    ("C03", "next change is the next raster cell < 5% of the time; changes uniform over cells (p > 0.05)",
     lambda: g("C03")["frac_next_in_raster"] < 0.05 and g("C03")["chi2_uniform_p"] > 0.05),
    ("C04", "every Reset gives a different starting grid",
     lambda: g("C04")["distinct_starts"] == g("C04")["n_starts"]),
    ("C05", "change probability flat across matching side-neighbours (spread <= 0.15); Area 1 non-4/5 >= 0.85",
     lambda: max(list(g("C05")["spread_area3"].values()) + list(g("C05")["spread_area1"].values())) <= 0.15
     and g("C05")["area1_nonterminal_min"] >= 0.85),
    ("C06", "Area 3: P(-> k) varies by <= 0.08 across old values",
     lambda: all(b - a <= 0.08 for a, b in g("C06")["ranges"].values())),
    ("C07", "Area 3: redraw probabilities roughly halve above 1 (ratios 0.4-0.55)",
     lambda: all(0.4 <= r <= 0.55 for r in g("C07")["ratios"])),
    ("C08", "Area 3: P(new=0) varies by <= 0.05 with number of zero neighbours",
     lambda: max(g("C08")["p_new0_by_zero_neighbours"].values()) - min(g("C08")["p_new0_by_zero_neighbours"].values()) <= 0.05),
    ("C09", "Area 3 held-out: same distribution (p > 0.05) and change count within 2% of prediction",
     lambda: g("C09")["chi2_p"] > 0.05 and abs(g("C09")["observed"] - g("C09")["predicted"]) / g("C09")["predicted"] < 0.02),
    ("C10", "values >= 10 appear only in Area 3",
     lambda: g("C10")["by_area"]["1"] == g("C10")["by_area"]["2"] == g("C10")["by_area"]["4"] == 0 and g("C10")["by_area"]["3"] > 0),
    ("C11", "every Area 4 change is an exact swap; value counts never change",
     lambda: g("C11")["exact"] == g("C11")["total"] and g("C11")["frames_with_changed_counts"] == 0),
    ("C12", "zero Area 4 swaps fail the 'strictly more matching 8-neighbours' test, in every dataset",
     lambda: all(g("C12")[k]["violations"] == 0 for k in ("discovery", "heldout", "group2"))
     and g("C12")["discovery"]["of_which_touch_boundary"] == g("C12")["discovery"]["improve_after_other_areas"]),
    ("C13", "only the 8-neighbour / no wrap / matching definition has zero exceptions",
     lambda: g("C13")["zero_exception_definitions"] == ["8-neighbour, no wrap, equal"]),
    ("C14", "Area 4 held-out swap share rises with the gain (+1 < 0.7, +5 > 0.8, never drops by > 0.05)",
     lambda: g("C14")["heldout"][0] < 0.7 and g("C14")["heldout"][4] > 0.8
     and all(b >= a - 0.05 for a, b in zip(g("C14")["heldout"], g("C14")["heldout"][1:]))),
    ("C15", "after step 200, predicted Area 4 swap rate within 0.01 of observed",
     lambda: all(abs(p - o) < 0.01 for k, (p, o) in g("C15")["windows"].items() if not k.startswith("0-"))),
    ("C16", "no Area 1 change outside 'advance' or 'jump to other branch start' (all datasets)",
     lambda: all(g("C16")[k].get("other", 0) == 0 for k in ("discovery", "heldout", "group2"))),
    ("C17", "Area 1 change count within 2% of prediction; 4/5 exit < 5%; >= 95% end as 4 or 5",
     lambda: abs(g("C17")["observed"] - g("C17")["predicted"]) / g("C17")["observed"] < 0.02
     and g("C17")["exit_rate_4_5"] < 0.05 and g("C17")["end_share_4_5"] >= 0.95),
    ("C18", "Area 1 first moves jump > 40%, later moves < 15% (both datasets)",
     lambda: all(g("C18")[d]["first move"][0] > 0.4 and g("C18")[d]["after an advance"][0] < 0.15 for d in ("discovery", "heldout"))),
    ("C18b", "high-branch later moves jump > 3x as often as low-branch later moves (both datasets)",
     lambda: all(g("C18b")[d]["high branch, later moves"][0] > 3 * g("C18b")[d]["low branch, later moves"][0] for d in ("discovery", "heldout"))),
    ("C19", "jump rate < 5% when the cell moved < 25 steps ago and > 15% after 300+ steps (both datasets)",
     lambda: all(g("C19")[d]["0"][0] < 0.05 and g("C19")[d]["300"][0] > 0.15 for d in ("discovery", "heldout"))),
    ("C20", "no neighbour direction/value pushes the Area 1 jump rate to 0% or 100% (stays within 5-50%)",
     lambda: g("C20")["per_direction_min"] > 0.05 and g("C20")["per_direction_max"] < 0.5),
    ("C21", "0 never changes in Area 2 (all datasets)",
     lambda: all(v == 0 for v in g("C21").values())),
    ("C22", "Area 2 rises seen == rises predicted by the mod-10 rule; zero violations",
     lambda: g("C22")["predicted_rises"] == g("C22")["seen_rises"] and all(v == 0 for v in g("C22")["violations"].values())),
    ("C23", "every Area 2 drop to a lower value is observed",
     lambda: g("C23")["drops_never_seen"] == []),
    ("C24", "Area 2 change probabilities agree between datasets within 0.1",
     lambda: all(abs(g("C24")["discovery"][k] - g("C24")["heldout"][k]) < 0.1 for k in g("C24")["discovery"])),
    ("C25", "Area 2: drop-to-0 rate rises with zero neighbours; neighbour-copy rate within 0.1 of control",
     lambda: list(g("C25")["p_drop_to_0_by_zero_neighbours"].values())[-1] > list(g("C25")["p_drop_to_0_by_zero_neighbours"].values())[0] + 0.3
     and g("C25")["new_in_own_nbrs"] - g("C25")["new_in_random_cell_nbrs"] < 0.1),
    ("C26", "Area 4 entropy never changes; Areas 1 and 2 fall below 1 bit",
     lambda: g("C26")["4"]["area4_max_change"] == 0 and g("C26")["1"]["end"] < 1 and g("C26")["2"]["end"] < 1),
    ("C27", "Area 3 settles within 0.1 bits of H(p)",
     lambda: abs(g("C27")["H_p"] - g("C27")["area3_end"]) < 0.1),
    ("C28", "rebuilt box: Areas 2-4 change counts within 10% and final entropies within 0.1 bits of held-out",
     lambda: all(abs(r["sim_changes"] - r["real_changes"]) / r["real_changes"] < 0.1 and abs(r["sim_end_entropy"] - r["real_end_entropy"]) < 0.1
                 for a, r in g("C28")["areas"].items() if a != "1")),
    ("C29", "rebuilt Area 2 final share of zeros within 5 points of real",
     lambda: abs(g("C29")["sim"]["area2_end_share_0"] - g("C29")["real"]["area2_end_share_0"]) < 0.05),
    ("C30", "branch-specific rates bring rebuilt Area 1's share of 4s closer to real than one shared rate",
     lambda: abs(g("C30")["split"] - g("C30")["real"]) < abs(g("C30")["shared"] - g("C30")["real"])),
    ("C31", "printed model tables: every Region 2 target row and the Region 3 table sum to exactly 1; all jump/swap rates in [0, 1]",
     lambda: all(abs(sum(r.values()) - 1) < 1e-9 for r in g("C31")["region2"]["target"].values())
     and abs(sum(g("C31")["region3"]["p"].values()) - 1) < 1e-9
     and all(0 <= v <= 1 for br in g("C31")["region1"]["jump"].values() for v in br.values())
     and all(0 <= v <= 1 for v in g("C31")["region4"]["accept"].values())),
    ("C32", "the WRITTEN model: change counts within 10% for all regions; final entropy within 0.1 bits for Regions 2-4",
     lambda: all(abs(g("C32")[f"changes_area{a}"]["model"] - g("C32")[f"changes_area{a}"]["real"]) / g("C32")[f"changes_area{a}"]["real"] < 0.1 for a in (1, 2, 3, 4))
     and all(abs(g("C32")[f"end_entropy_area{a}"]["model"] - g("C32")[f"end_entropy_area{a}"]["real"]) < 0.1 for a in (2, 3, 4))),
    ("C33", "Region 3: the free table beats every standard family by > 10 AIC points; Poisson fits worst",
     lambda: g("C33")["aic_gap_to_table"] > 10
     and max((v["aic"], k) for k, v in g("C33")["families"].items())[1] == "Poisson(lam)"),
    ("C34", "worked examples obey the written rules (Region 1 advance/jump, Region 2 allowed rise, Region 4 gain >= 1)",
     lambda: abs(g("C34")["region1_advance"]["new"] - g("C34")["region1_advance"]["old"]) == 1
     and g("C34")["region1_jump"]["new"] in (0, 9)
     and g("C34")["region2_rise"]["new"] in {(g("C34")["region2_rise"]["old"] * k) % 10 for k in range(10)}
     and g("C34")["region4_swap"]["gain"] >= 1),
    ("C35", "Region 1 gates predict jump vs advance for every held-out change from 0-3 or 6-9",
     lambda: g("C35")["correct"] == g("C35")["n"] > 10000),
    ("C36", "Region 1 cells at 4/5 never jump while their gate agrees; jump at about the pick rate (0.008-0.013) when it disagrees",
     lambda: g("C36")["agree_jumps"] == 0 and 0.008 <= g("C36")["disagree_rate"] <= 0.013),
    ("C37", "the waiting-time rule is clearly worse than the gates (best guess < 95% right)",
     lambda: g("C37")["correct"] / g("C37")["n"] < 0.95),
    ("C38", "Region 2 minimum part never rises, and every new value is present in rows 11-20",
     lambda: g("C38")["rises"] == 0 and g("C38")["partner_found"] == g("C38")["changes"] > 1000),
    ("C39", "every Region 2 multiply-part change equals (old x a value in that part) mod 10",
     lambda: g("C39")["product_found"] == g("C39")["changes"] > 1000),
    ("C40", "the strict Region 4 rule holds for every held-out swap when Regions 1-3 move first",
     lambda: g("C40")["strict_in_order"] == g("C40")["swaps"] > 1000),
    ("C41", "rebuilt model within 10% of the held-out runs on cells changed per region, and within 0.1 bits on end entropy",
     lambda: all(abs(v["model"] - v["real"]) <= 0.10 * v["real"] for k, v in g("C41")["table"].items() if k.endswith("_changed"))
     and all(abs(v["model"] - v["real"]) <= 0.1 for k, v in g("C41")["table"].items() if "entropy" in k)),
    ("C42", "the first step after Reset follows the Region 1 gates in every Group 1 run",
     lambda: g("C42")["r1_gate_ok"] == g("C42")["r1_changes"] > 0 and g("C42")["transitions"] == 61),
    ("C43", "late Region 1 activity matches the rebuilt box in blocks A-C (within 15%) and is higher in block D",
     lambda: all(abs(v["real"] - v["model"]) <= 0.15 * v["model"] for k, v in g("C43")["by_block"].items() if k != "D")
     and g("C43")["by_block"]["D"]["real"] > 1.3 * g("C43")["by_block"]["D"]["model"]),
    ("C44", "deductions: Region 3 repeat chance about 0.28 and table entropy about 2.14 bits; Region 1 block with LOW inputs has stable states with 1, 2, 6 and 9 HIGH cells",
     lambda: abs(g("C44")["r3_same"] - 0.276) < 0.01 and abs(g("C44")["r3_entropy"] - 2.14) < 0.02 and g("C44")["r1_stable_states"]["000"] == [1, 2, 6, 9]),
    ("C45", "every rule holds on the fresh runs (Region 1, settled cells, both Region 2 parts, Region 4)",
     lambda: g("C45")["gate_ok"] == g("C45")["n"] > 0 and g("C45")["settled"]["agree"][1] == 0
     and g("C45")["pt"]["rises"] == 0 and g("C45")["pt"]["partner_found"] == g("C45")["pt"]["changes"]
     and g("C45")["fo"]["product_found"] == g("C45")["fo"]["changes"]
     and g("C45")["sw"]["strict_in_order"] == g("C45")["sw"]["swaps"]),
    ("C46", "a 10-step press changes at most 10 cells per region and keeps Region 4's counts",
     lambda: max(g("C46")["max_cells_per_press"].values()) <= 10 and g("C46")["region4_counts_constant"]),
    ("C47", "fresh runs: block D comparison recorded for every fresh run",
     lambda: g("C47")["n_real"] >= 5),
    ("C48", "values 10-13 occur only in Region 3, within a factor of 2 of the table's rate",
     lambda: g("C48")["by_dataset"] and all(v["outside_region3"] == 0 for v in g("C48")["by_dataset"].values())
     and 0.5 <= g("C48")["observed"] / g("C48")["predicted"] <= 2),
    ("C49", "whole-grid value shares deduced from the rules are within 1% of the measured shares (D and H)",
     lambda: g("C49")["D"]["maxerr"] < 0.01 and g("C49")["H"]["maxerr"] < 0.01),
    ("C50", "Region 3 neighbour pairs differ at the deduced rate 1 - sum p^2 (within 0.02); Regions 1, 2 and 4 fall below their start",
     lambda: abs(g("C50")["end"]["3"] - g("C50")["r3_pred"]) < 0.02
     and all(g("C50")["end"][a] < g("C50")["start"][a] - 0.2 for a in ("1", "2", "4"))),
    ("C51", "Region 4 matching pairs never fall in steps where only Region 4 and no outside neighbour changed",
     lambda: g("C51")["fell"] == 0 and g("C51")["rose"] == g("C51")["steps"] > 1000),
    ("C52", "predicting 'nothing changes' is right for more than 99% of cells per step",
     lambda: g("C52")["D"] > 0.99 and g("C52")["H"] > 0.99),
    ("C53", "Region 1 reads the grid before Regions 2-4 move in every case that can tell; no case tells Regions 2 and 3 apart",
     lambda: g("C53")["r1"]["cases"] > 0 and g("C53")["r1"]["before"] == g("C53")["r1"]["cases"] and g("C53")["r2"]["cases"] == 0),
]

lines = [f"{'claim':6s} {'result':6s} {'source':22s} condition"]
n_fail = 0
for cid, text, fn in CHECKS:
    try:
        ok = bool(fn())
    except Exception as e:  # missing metric = not proven
        ok = False; text += f"  [error: {e!r}]"
    n_fail += not ok
    lines.append(f"{cid:6s} {'PASS' if ok else 'FAIL':6s} {M.get(cid, ('missing',))[0]:22s} {text}")
lines.append(f"\n{len(CHECKS) - n_fail}/{len(CHECKS)} claims pass.")
out = "\n".join(lines)
print(out)
(ROOT / "results" / "claims_check.txt").write_text(out + "\n")
raise SystemExit(1 if n_fail else 0)
