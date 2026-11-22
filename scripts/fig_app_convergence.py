#!/usr/bin/env python3
"""Appendix figure of main.tex: the uniform mean free path test of the moment
transport against the analytic transfer functions, at every resolution run.

usage: fig_app_convergence.py [--variants]
reads data/convergence/T_N<N>_l{4,1}.txt (tools/analysis/moment_transfer.py of
NewRadHydroCode, branch moment-order2), writes figures/fig_app_convergence.{pdf,png}

Columns: M1, OTVET, rays. Rows: lambda = L/4, lambda = L. Per resolution: the code
with the default settings (first order, inject after the transport), and the
exact linear solution of the discrete scheme (data/convergence/Tlin_N*.txt,
scripts/transfer_exact_linear.py). --variants adds, at the reference
resolution of each row, injection before the transport (with its exact
linear solution) and second order.

Rays (third column): data/convergence/T_rays_N128_l{4,1}.txt (tools/analysis/
ray_transfer.cpp, branch rt-convergence-runs; sources in one cell in 512) at
ray pool sizes of 8, 15, 64 and 120 per cell, with the exact solution plus
white shot noise of rms SIG0 / sqrt(rays per cell) per cell (scripts/ray_noise.py;
rays per cell from data/convergence/rays_pool.txt).
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
POOLS = (8, 15, 64, 120)
RCOL = {8: "#f2b28a", 15: "#e57a3c", 64: "#b24a17", 120: "#6b2706"}  # a second hue, light to dark
SIG0 = 0.95  # rms per cell of the ray noise times sqrt(rays per cell), scripts/ray_noise.py
SRC = 512.0  # cells per source in the ray test: P_L / Lbar^2 = SRC cells


def load(N, frac, stem="T"):
    f = os.path.join(here, "..", "data", "convergence", "%s_N%d_l%d.txt" % (stem, N, frac))
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


pool = {ln.split()[0]: float(ln.split()[1])
        for ln in open(os.path.join(here, "..", "data", "convergence", "rays_pool.txt"))}
fig, ax = plt.subplots(2, 3, figsize=(10.4, 5.7), sharex="row", sharey="row")
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
            t = np.loadtxt(os.path.join(here, "..", "data", "convergence", "Tlin_N%d_l%d.txt" % (N, frac)))
            jc = 1 if m == "m1" else 3  # columns: k lam, m1 inj1, m1 inj0, otvet inj1, otvet inj0
            p.loglog(t[:, 0], t[:, jc], color=COL[N], lw=1.1, zorder=2.5)
            if variants and N == NREF:
                p.loglog(t[:, 0], t[:, jc + 1], color=COL[N], lw=1.1, ls=(0, (1, 1.2)), zorder=2.5)
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
    # the rays
    p = ax[ir, 2]
    d = load(NREF, frac, "T_rays")
    kl = d["k*lam"]
    kk = np.geomspace(kmin, kl.max() * 1.05, 300)
    ex = np.arctan(kk) / kk
    p.loglog(kk, ex, "k-", lw=1.8, zorder=2)
    for f in POOLS:
        nray = pool["rays_N%d_l%d_f%d" % (NREF, frac, f)]
        p.loglog(kk, np.sqrt(ex ** 2 + SIG0 ** 2 / nray / SRC), color=RCOL[f], lw=1.1, zorder=2.5)
        p.loglog(kl, d["rays_f%d" % f], ls="none", marker="o", ms=4.2, color=RCOL[f], mec="white", mew=0.5, zorder=3)
    p.loglog(kl, d["rays_f15_avg"], ls="none", marker="o", ms=4.6, mfc="none", mec=RCOL[15], mew=1.0, zorder=4)
    p.text(0.97, 0.94, r"rays, $\lambda=L%s$" % ("/4" if frac == 4 else ""), transform=p.transAxes,
           ha="right", va="top", fontsize=10)
    p.tick_params(which="both", direction="in", top=True, right=True, labelsize=8.5)
    p.set_xlabel(r"$k\lambda$", fontsize=10)

h = [Line2D([], [], color="k", lw=1.8, label=r"$(k\lambda)^{-1}\arctan(k\lambda)$"),
     Line2D([], [], color="0.4", ls="--", lw=1.4, label="closure's linear theory")]
h += [Line2D([], [], ls="none", marker="o", ms=4.5, color=COL[N], label=r"code, $%d^3$" % N) for N in NS]
ax[0, 0].legend(handles=h, fontsize=7.4, loc="lower left", frameon=False, handlelength=1.8, labelspacing=0.35)
h = [Line2D([], [], color=COL[NREF], lw=1.1, label="linear theory of the\ndiscretized equations")]
if variants:
    h += [Line2D([], [], ls="none", marker="o", ms=4.6, mfc="none", mec=COL[NREF], label=r"inject before, $%d^3$" % NREF),
          Line2D([], [], ls="none", marker="s", ms=4.6, mfc="none", mec=COL[NREF], label=r"$2^{\rm nd}$ order solver, $%d^3$" % NREF)]
ax[1, 0].legend(handles=h, fontsize=7.4, loc="lower left", frameon=False, handlelength=1.8, labelspacing=0.35)
h = [Line2D([], [], ls="none", marker="o", ms=4.5, color=RCOL[f],
            label=r"rays, $%d^3$, pool %d%s" % (NREF, f, {15: " (suite)", 64: " (original)"}.get(f, ""))) for f in POOLS]
ax[0, 2].legend(handles=h, fontsize=7.4, loc="lower left", frameon=False, handlelength=1.8, labelspacing=0.35)
h = [Line2D([], [], color=RCOL[15], lw=1.1, label="arctan with shot noise\nof the rays"),
     Line2D([], [], ls="none", marker="o", ms=4.6, mfc="none", mec=RCOL[15], label="pool 15, mean of 16 substeps")]
ax[1, 2].legend(handles=h, fontsize=7.4, loc="lower left", frameon=False, handlelength=1.8, labelspacing=0.35)
fig.tight_layout(h_pad=0.6, w_pad=0.4)
out = os.path.join(here, "..", "figures", "fig_app_convergence")
fig.savefig(out + ".pdf")
fig.savefig(out + ".png", dpi=170)
