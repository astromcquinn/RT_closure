#!/usr/bin/env python3
"""The one-point distribution of Gamma_HI after overlap and the tau_eff
scatter of every RT method.

Left: the volume-weighted PDF of log10(Gamma/<Gamma>_V) at z = 4.99, the
    last panel of data/pdf_gamma.txt.
Right: tau_eff(84 %) - tau_eff(16 %) over 50 Mpc/h segments with tau
    rescaled to Bosman et al. 2022's mean flux, and their observed widths
    (squares); the right panel of fig_mfp_width.py, see its docstring.

    Brown, open symbols: the rays' run with (each rescaled to the same mean
    flux; the w_uG, w_uGT, w_ion columns of data/taueff_temp.txt)
      dashed, circles     a uniform Gamma_HI: x_HI of the cells with
                          x_HI < 1e-2 scaled to their median Gamma
      dash-dot, triangles also a uniform temperature of those cells: x_HI
                          scaled by (T/T_ref)^0.7, Doppler width at T_ref
      dotted, diamonds    also no neutral gas: the other cells at T_ref and
                          in equilibrium with Gamma_ref

Data: data/pdf_gamma.txt, data/taueff_mfp_snap_A.txt, data/taueff_width_obs.txt,
data/taueff_temp.txt.

usage: python3 scripts/fig_pdf_width.py   (writes figures/fig_pdf_width.{pdf,png})
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import fig_mfp_width as fm  # noqa: E402
import fig_pk  # noqa: E402

DATA, OBS = fm.DATA, fm.OBS
TEST = "#8c5a2e"  # the rays' test curves: a colour no run and no measurement uses


def main():
    head, dp, _ = fig_pk.read_pdf(os.path.join(DATA, "pdf_gamma.txt"))[-1]
    zpdf = float(head.split("z = ")[1].split()[0].rstrip(";"))
    width, _ = fm.read_runs(os.path.join(DATA, "taueff_mfp_snap_A.txt"))
    wo = fm.read_width_obs(os.path.join(DATA, "taueff_width_obs.txt"))
    plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.8, "text.color": fm.INK,
                         "axes.edgecolor": fm.INK2, "xtick.color": fm.INK2, "ytick.color": fm.INK2})
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for key, label, c, ls, lw in fig_pk.RUNS:
        if key in dp:
            a0.plot(*dp[key], color=c, ls=ls, lw=lw, label=label)
        if key in width:
            d = width[key]
            a1.plot(d[:, 0], d[:, 1], color=c, ls=ls, lw=lw, marker="o", ms=3.5)
    uni = np.array(sorted([float(v) for v in l.split()[1:]] for l in open(os.path.join(DATA, "taueff_temp.txt"))
                          if l.startswith("rays ")))
    for col, ls, mk, label in ((9, (0, (5, 2)), "o", r"rays, uniform $\Gamma_{\rm HI}$"),
                               (15, (0, (4, 1.5, 1, 1.5)), "v", r"rays, uniform $\Gamma_{\rm HI}$ and $T$"),
                               (18, (0, (1, 1.5)), "D", r"rays, uniform $\Gamma_{\rm HI}$, $T$, no neutral gas")):
        a1.plot(uni[:, 0], uni[:, col], color=TEST, ls=ls, lw=1.1, marker=mk, ms=3.4, mfc="white", mew=0.9,
                zorder=3, label=label)
    a1.legend(fontsize=6.5, frameon=False, loc="upper right", handlelength=3.8)
    a1.errorbar(wo[:, 0], wo[:, 1], yerr=[wo[:, 1] - wo[:, 2], wo[:, 3] - wo[:, 1]], fmt="s", ms=4,
                color=OBS, mfc="white", ecolor=OBS, elinewidth=0.8, capsize=2, zorder=5)
    for z, w0, _, _, w1 in wo:
        if w1 > w0 * 1.02:
            top = w1 if np.isfinite(w1) else 3.6
            a1.plot([z, z], [w0, top], ls=":", color=OBS, lw=0.9, zorder=4)
            a1.plot([z], [top], marker="^" if not np.isfinite(w1) else "_", color=OBS, ms=4, zorder=4)
    a0.set_yscale("log")
    a0.set_ylim(1e-3, 20)
    a0.set_xlim(-1.2, 1.2)
    a0.set_xlabel(r"$\log_{10}(\Gamma_{\rm HI}/\langle\Gamma_{\rm HI}\rangle_V)$")
    a0.set_ylabel(r"$dP/d\log_{10}\Gamma_{\rm HI}$")
    a0.text(0.04, 0.94, f"$z={zpdf:.2f}$", transform=a0.transAxes, va="top")
    a0.legend(fontsize=6.5, frameon=False, loc="upper right", handlelength=2.6)
    fm.log_axis(a1, [0.5, 0.7, 1, 1.5, 2, 3])
    a1.set_ylim(0.4, 3.8)
    a1.set_xlim(fm.ZMIN, fm.ZMAX)
    a1.invert_xaxis()
    a1.set_xlabel(r"$z$")
    a1.set_ylabel(r"$\tau_{\rm eff}(84\%)-\tau_{\rm eff}(16\%)$, $\langle F\rangle$ = observed")
    for ax in (a0, a1):
        ax.grid(alpha=0.3, lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = os.path.join(fm.HERE, "..", "figures", "fig_pdf_width")
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


if __name__ == "__main__":
    main()
