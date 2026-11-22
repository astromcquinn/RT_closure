#!/usr/bin/env python3
"""Appendix figure of main.tex: the uniform mean free path test of the moment
transport against the analytic transfer functions, at every resolution run.

usage: fig_app_convergence.py [--variants]
reads data/convergence/T_N<N>_l{4,1}.txt (tools/analysis/moment_transfer.py of
NewRadHydroCode, branch moment-order2), writes figures/fig_app_convergence.{pdf,png}

Columns: M1, OTVET. Rows: lambda = L/4, lambda = L. Per resolution: the code
with the default settings (first order, inject after the transport), and the
band between the linear solution with the scheme's numerical diffusion and
the same with the injection floor. --variants adds, at the reference
resolution of each row, injection before the transport and second order.
"""
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

here = os.path.dirname(os.path.abspath(__file__))
variants = "--variants" in sys.argv
NS = (32, 64, 128, 256)
COL = {32: "#86b6ef", 64: "#3987e5", 128: "#1c5cab", 256: "#0d366b"}  # one hue, light to dark
NREF = 128  # resolution of the variants


def load(N, frac):
    f = os.path.join(here, "..", "data", "convergence", "T_N%d_l%d.txt" % (N, frac))
    if not os.path.exists(f):
        return None
    hdr = [ln for ln in open(f) if ln.startswith("# k*lam")][0]
    names = re.split(r"\s{2,}", hdr[2:].strip())
    a = np.array([[float(x) for x in ln.replace("(", " ").replace(")", " ").split()]
                  for ln in open(f) if not ln.startswith("#")])
    d = {n: a[:, i] for i, n in enumerate(names[:8])}
    for j, n in enumerate(names[8:]):
        n = re.sub(r"_N\d+_l\d", "", n)
        d[n], d["r_" + n] = a[:, 8 + 2 * j], a[:, 9 + 2 * j]
    return d


fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.9), sharex="row", sharey="row")
for ir, frac in enumerate((4, 1)):
    for ic, (m, lin, glf, name) in enumerate((("m1", "M1 lin", "M1 lin+GLF", "M1"),
                                              ("otvet", "OTVET lin", "OTVET lin+GLF", "OTVET"))):
        p = ax[ir, ic]
        fine = None
        for N in NS:
            d = load(N, frac)
            if d is None:
                continue
            fine = d
            lam = N / frac
            f = 1 - np.exp(-1 / lam)
            kl = d["k*lam"]
            p.fill_between(kl, d[glf], d[glf] + f * (1 - d[glf]), color=COL[N], alpha=0.22, lw=0)
            p.loglog(kl, d[m + "_inj1_o1"], ls="none", marker="o", ms=4.2, color=COL[N], mec="white", mew=0.5, zorder=3)
            if variants and N == NREF:
                for key, mk in ((m + "_inj0_o1", "o"), (m + "_inj1_o2", "s")):
                    ok = d["r_" + key] > 0.5
                    p.loglog(kl[ok], d[key][ok], ls="none", marker=mk, ms=4.6, mfc="none", mec=COL[N], mew=1.0, zorder=4)
        # analytic curves on the finest grid's k range, extended to the coarsest's first bin
        kmin = fine["k*lam"].min() * 0.75
        kk = np.geomspace(kmin, fine["k*lam"].max() * 1.05, 300)
        p.loglog(kk, np.arctan(kk) / kk, "k-", lw=1.8, zorder=2)
        cont = 1 / (1 + kk ** 2 / 3)
        if m == "otvet":
            cont *= 1 + 2 * np.pi ** 2 * kk / (3 * 7.66 * frac)  # lambda / L_O = 1 / (7.66 frac)
        p.loglog(kk, cont, color="0.4", ls="--", lw=1.4, zorder=2)
        p.set_ylim(2e-4 if frac == 4 else 3e-5, 1.5)
        p.set_xlim(kmin, fine["k*lam"].max() * 1.1)
        p.text(0.97, 0.94, r"%s, $\lambda=L%s$" % (name, "/4" if frac == 4 else ""), transform=p.transAxes,
               ha="right", va="top", fontsize=10)
        p.tick_params(which="both", direction="in", top=True, right=True, labelsize=8.5)
        if ic == 0:
            p.set_ylabel(r"$T(k)$", fontsize=10)
        p.set_xlabel(r"$k\lambda$", fontsize=10)

h = [Line2D([], [], color="k", lw=1.8, label="exact"),
     Line2D([], [], color="0.4", ls="--", lw=1.4, label="closure, continuum")]
h += [Line2D([], [], ls="none", marker="o", ms=4.5, color=COL[N], label=r"code, $%d^3$" % N) for N in NS]
ax[0, 0].legend(handles=h, fontsize=7.4, loc="lower left", frameon=False, handlelength=1.8, labelspacing=0.35)
h = [Patch(color=COL[128], alpha=0.3, lw=0, label="closure + numerical\ndiffusion (to + floor)")]
if variants:
    h += [Line2D([], [], ls="none", marker="o", ms=4.6, mfc="none", mec=COL[NREF], label=r"inject before, $%d^3$" % NREF),
          Line2D([], [], ls="none", marker="s", ms=4.6, mfc="none", mec=COL[NREF], label=r"second order, $%d^3$" % NREF)]
ax[1, 0].legend(handles=h, fontsize=7.4, loc="lower left", frameon=False, handlelength=1.8, labelspacing=0.35)
fig.tight_layout(h_pad=0.6, w_pad=0.4)
out = os.path.join(here, "..", "figures", "fig_app_convergence")
fig.savefig(out + ".pdf")
fig.savefig(out + ".png", dpi=170)
