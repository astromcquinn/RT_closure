#!/usr/bin/env python3
"""Uniform mean free path test of the moment transport against the analytic
transfer function, with the model of the scheme's numerical diffusion
(convergence.tex, Fig. 1).

usage: fig_transfer_diffusion.py [N]      (default 128)
reads data/convergence/T_N<N>_l{4,1}.txt (tools/analysis/moment_transfer.py of
NewRadHydroCode, branch moment-order2), writes figures/convergence/fig_transfer_diffusion.{pdf,png}
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 128


def load(frac):
    rows = []
    for line in open(os.path.join(here, "..", "data", "convergence", "T_N%d_l%d.txt" % (N, frac))):
        if line.startswith("#"):
            continue
        t = line.replace("(", " ").replace(")", " ").split()
        rows.append([float(x) for x in t])
    a = np.array(rows)
    # k lam, exact, M1 lin, M1 lin+GLF, OTVET lin, OTVET lin+GLF, M1 lin+2nd, OTVET lin+2nd, then (T, r) of
    # m1 i1 o1, m1 i1 o2, m1 i0 o1, m1 i0 o2, otvet i1 o1, otvet i1 o2, otvet i0 o1, otvet i0 o2
    runs = {}
    for j, name in enumerate(["m1_i1_o1", "m1_i1_o2", "m1_i0_o1", "m1_i0_o2",
                              "otvet_i1_o1", "otvet_i1_o2", "otvet_i0_o1", "otvet_i0_o2"]):
        runs[name] = (a[:, 8 + 2 * j], a[:, 9 + 2 * j])
    return a, runs


fig, ax = plt.subplots(2, 2, figsize=(10.5, 8.2), sharex="col")
c1, c2 = "#0072B2", "#D55E00"
for ic, frac in enumerate((4, 1)):
    a, runs = load(frac)
    kl, exact = a[:, 0], a[:, 1]
    lam = N / frac
    floor = 1 - np.exp(-1 / lam)
    for ir, (m, lin, glf, mus) in enumerate((("m1", a[:, 2], a[:, 3], a[:, 6]), ("otvet", a[:, 4], a[:, 5], a[:, 7]))):
        p = ax[ir, ic]
        p.loglog(kl, exact, "k-", lw=2, label=r"exact, $\arctan(k\lambda)/k\lambda$")
        p.loglog(kl, lin, color="0.45", ls="--", lw=1.6, label="closure, continuum")
        p.loglog(kl, glf, color=c1, lw=1.2, label="closure + first-order diffusion")
        p.loglog(kl, glf + floor * (1 - glf), color=c1, lw=1.2, ls=":", label="... + injection floor")
        p.loglog(kl, mus, color=c2, lw=1.2, label="closure + second-order scheme")
        p.loglog(kl, mus + floor * (1 - mus), color=c2, lw=1.2, ls=":", label="... + injection floor")
        for name, col, mk, fill, lab in ((m + "_i1_o1", c1, "o", True, "code, order 1"),
                                         (m + "_i0_o1", c1, "o", False, "code, order 1, inject before"),
                                         (m + "_i1_o2", c2, "s", True, "code, order 2"),
                                         (m + "_i0_o2", c2, "s", False, "code, order 2, inject before")):
            T, r = runs[name]
            ok = r > 0.5  # below: the response is uncorrelated or anticorrelated with the sources
            p.loglog(kl[ok], T[ok], ls="none", marker=mk, ms=5.5, color=col, mfc=col if fill else "none", label=lab)
            p.loglog(kl[~ok], T[~ok], ls="none", marker="x", ms=5, color=col)
        p.axvline(lam, color="0.6", lw=0.6)
        p.text(lam, 0.96, r"$k\Delta x=1$ ", transform=p.get_xaxis_transform(), ha="right", va="top", fontsize=8, color="0.4")
        p.set_title(("M1" if m == "m1" else "OTVET") + r", $\lambda=L%s$ (%d cells), $%d^3$" % ("/4" if frac == 4 else "", lam, N),
                    fontsize=10)
        p.set_ylim(max(1e-4, 0.3 * min(lin.min(), exact.min())), 1.5)
        if ir == 1:
            p.set_xlabel(r"$k\lambda$")
        if ic == 0:
            p.set_ylabel(r"$T(k)=(P_N/P_L)^{1/2}$")
ax[0, 0].legend(fontsize=7.5, loc="lower left")
fig.tight_layout()
out = os.path.join(here, "..", "figures", "convergence", "fig_transfer_diffusion")
fig.savefig(out + ".pdf")
fig.savefig(out + ".png", dpi=140)
