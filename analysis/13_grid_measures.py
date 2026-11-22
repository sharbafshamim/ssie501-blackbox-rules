"""13 - Whole-grid and neighbour measures: value shares, boundary density, a Region 4 energy function, baseline accuracy.

Claims proven here: C49-C53.
  C53  what the data say about the update order inside one step
  C49  whole-grid value distribution at step 2,000: deduced from the rules vs measured; curve fits for comparison
  C50  boundary density per region; Region 3's value is deduced from its table alone
  C51  Region 4's matching-pair count never falls when only Region 4 moves (a Lyapunov function)
  C52  copying the previous grid already gets 99.7% of cells right, so we score changes, not cells
Run:  python analysis/13_grid_measures.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import matplotlib.pyplot as plt
from blackbox.data import load_discovery, load_heldout
from blackbox.regions import AREA, MASK
from blackbox.gate_model import R3_TABLE, r1_target_grid, PT
from blackbox.data import load_group2
from blackbox.report import Log, FIGURES

log = Log("13_grid_measures")
D, H = load_discovery(), load_heldout()
BOTH = [("D", D), ("H", H)]

# C49: whole-grid distribution, deduced vs measured
p3 = R3_TABLE[:12]
c50 = {}
for name, runs in BOTH:
    st = np.array([h[0] for h in runs]); fin = np.array([h[-1] for h in runs])
    meas = np.bincount(fin.ravel(), minlength=14)[:12] / fin.size
    a1 = np.bincount(fin[:, MASK[1]].ravel(), minlength=14)[:12] / (len(runs) * 100)   # measured 4/5 split
    a2 = np.eye(12)[0]                                                                  # all zeros
    a4 = np.bincount(st[:, MASK[4]].ravel(), minlength=14)[:12] / (len(runs) * 100)    # swaps keep the start mix
    pred = (a1 + a2 + p3 + a4) / 4
    v = np.sort(meas[:10])[::-1]; k = np.arange(1, 11)
    b, a = np.polyfit(np.log(k), np.log(v), 1); yp = np.exp(a) * k ** b
    b2, a2_ = np.polyfit(k, np.log(v), 1); ye = np.exp(a2_ + b2 * k)
    r2 = lambda y: 1 - ((v - y) ** 2).sum() / ((v - v.mean()) ** 2).sum()
    c50[name] = dict(meas=meas, pred=pred, maxerr=float(np.abs(meas - pred).max()),
                     pl_exp=float(-b), pl_r2=float(r2(yp)), ex_ratio=float(np.exp(-b2)), ex_r2=float(r2(ye)))
log.claim("C49", "Value shares over the whole grid at the last step, deduced from the rules (Region 2 all 0, Region 3 its table, "
          "Region 4 its starting mix; only Region 1's 4/5 split taken from data) vs measured: largest gap "
          + ", ".join(f"{n} {c50[n]['maxerr']:.2%}" for n, _ in BOTH) + f"; value 0 {c50['H']['meas'][0]:.1%} measured, "
          f"{c50['H']['pred'][0]:.1%} deduced (H). A power-law fit to the ranked shares also scores well (R2 "
          + ", ".join(f"{n} {c50[n]['pl_r2']:.2f}" for n, _ in BOTH) + ") without saying anything about the mechanism.",
          **{n: c50[n] for n, _ in BOTH})


# C50: boundary density per region over time
def density(g, a):
    m = MASK[a]; hh = m[:, 1:] & m[:, :-1]; vv = m[1:] & m[:-1]
    return (((g[:, 1:] != g[:, :-1]) & hh).sum() + ((g[1:] != g[:-1]) & vv).sum()) / (hh.sum() + vv.sum())


ts = np.arange(0, 2000, 20)
curves = {a: np.mean([[density(h[t], a) for t in ts] for _, rs in BOTH for h in rs], axis=0) for a in (1, 2, 3, 4)}
r3_pred = float(1 - (R3_TABLE ** 2).sum())
start = {a: float(curves[a][0]) for a in curves}; end = {a: float(curves[a][-1]) for a in curves}
log.claim("C50", "Share of side-by-side neighbour pairs with different values (D + H, 91 runs), start -> step 1,980: "
          + "; ".join(f"Region {a} {start[a]:.2f} -> {end[a]:.2f}" for a in (1, 2, 3, 4))
          + f". Region 3 deduced from its table alone: 1 - sum p^2 = {r3_pred:.3f}.",
          start=start, end=end, r3_pred=r3_pred)

# C51: Region 4 Lyapunov function
OFF = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
pairs = set()
for r, c in np.argwhere(MASK[4]):
    for dr, dc in OFF:
        if 0 <= r + dr < 20 and 0 <= c + dc < 20:
            pairs.add(tuple(sorted([r * 20 + c, (r + dr) * 20 + c + dc])))
P = np.array(sorted(pairs)); m4 = MASK[4].ravel()
halo = np.zeros(400, bool); halo[[x for x in P.ravel() if not m4[x]]] = True
steps = fell = rose = 0
for _, rs in BOTH:
    for h in rs:
        f = h.reshape(len(h), 400); L = (f[:, P[:, 0]] == f[:, P[:, 1]]).sum(1); d = np.diff(L)
        sel = (f[1:, m4] != f[:-1, m4]).any(1) & ~(f[1:, halo] != f[:-1, halo]).any(1)
        steps += int(sel.sum()); fell += int((d[sel] < 0).sum()); rose += int((d[sel] > 0).sum())
log.claim("C51", f"Matching neighbour pairs touching Region 4: in {steps:,} steps where Region 4 swapped and no neighbouring "
          f"cell outside it changed, the count rose {rose:,} times and fell {fell} times. It is bounded, so swaps must stop.",
          steps=steps, rose=rose, fell=fell)

# C52: persistence baseline
acc = {n: float(np.mean([(h[1:] == h[:-1]).mean() for h in rs])) for n, rs in BOTH}
log.claim("C52", "Predicting 'nothing changes' gets " + ", ".join(f"{n} {acc[n]:.2%}" for n in acc)
          + " of cells right per step, so cell accuracy cannot tell models apart; we score every recorded change instead.",
          **acc)


# C53: update order inside one step
a = dict(cases=0, before=0, after=0); b = dict(cases=0)
G2 = load_group2()
R1 = AREA == 1
for h in D + H + G2:
    for t in range(len(h) - 1):
        g0, g1 = h[t], h[t + 1]; ch = g0 != g1; other = ch & ~R1
        if (ch & R1).any() and other.any():
            gn = g0.copy(); gn[other] = g1[other]
            T0, Tn = r1_target_grid(g0), r1_target_grid(gn)
            for r, c in np.argwhere(ch & R1):
                v, w = int(g0[r, c]), int(g1[r, c])
                if v in (4, 5) or T0[r, c] == Tn[r, c]:
                    continue
                high = v >= 5; jump = w == (0 if high else 9)
                a["cases"] += 1; a["before"] += int((T0[r, c] != int(high)) == jump); a["after"] += int((Tn[r, c] != int(high)) == jump)
        pc = ch & PT
        if pc.any():
            r, c = np.argwhere(pc)[0]; gn = g0.copy(); m = ch & ((AREA == 3) | (AREA == 4)); gn[m] = g1[m]
            w = int(g1[r, c])
            b["cases"] += int((w in set(g0[10:20].ravel().tolist())) != (w in set(gn[10:20].ravel().tolist())))
log.claim("C53", f"Update order (D, H, G2): Region 1 changes whose gate gives a different answer depending on whether Regions 2-4 have "
          f"already moved in that step: {a['cases']}; the gate read before they move is right in {a['before']}, after in {a['after']}. "
          f"Region 2 minimum-part changes that depend on whether Region 3 or 4 moved first: {b['cases']}, so the order of Regions 2 and 3 "
          f"cannot be told from the data. Region 4 after Regions 2 and 3: see C40.", r1=a, r2=b)

# figure
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
cols = {1: "#3D6FD8", 2: "#E0703E", 3: "#1F9E72", 4: "#6B55CC"}
for a in (1, 2, 3, 4):
    ax[0].plot(ts, curves[a], color=cols[a], label=f"Region {a}")
ax[0].axhline(r3_pred, color=cols[3], ls="--", lw=1); ax[0].text(1990, r3_pred + 0.02, "Region 3 deduced", ha="right", color=cols[3], fontsize=8)
ax[0].set(title="Neighbour pairs with different values", xlabel="step", ylabel="share of pairs", ylim=(0, 1)); ax[0].legend()
x = np.arange(10); w = 0.4
ax[1].bar(x - w / 2, c50["H"]["meas"][:10], w, color="#1E2330", label="measured (H, step 2,000)")
ax[1].bar(x + w / 2, c50["H"]["pred"][:10], w, color="#8A93A6", label="deduced from the rules")
ax[1].set(title="Value shares over the whole grid", xlabel="value", xticks=x); ax[1].legend()
fig.tight_layout(); fig.savefig(FIGURES / "13_grid_measures.png")
log.save()
