#!/usr/bin/env python3
"""The reionization history, the median photoionization rate and the
one-point distribution of Gamma_HI after overlap, for every run.

  left:   x_HII,V (solid) and x_HII,M (dashed) against z
  middle: the median Gamma_HI of the ionised cells (x_HI < 1e-2) against z,
          with the measurements of Gaikwad et al. 2023 (data/gamma_obs.txt)
  right:  the volume-weighted PDF of log10(Gamma/<Gamma>_V) at z = 4.99, the
          last panel of data/pdf_gamma.txt

Data: data/history.txt, one line per run and snapshot,
  label  z  xHII_V  xHII_M  GammaHI_ion_med[s^-1]
(labels as in data/pk_suite.txt: rays M1 OTVET split screen cone rays_A+RR;
'#' lines are comments), and data/pdf_gamma.txt.

usage: python3 scripts/fig_history.py [--history PATH]
       (writes figures/fig_history.{pdf,png})
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import fig_pk  # noqa: E402  (the paper's run colours and the PDF reader)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")
OBS = "#6b6a66"


def read_history(path):
    out = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        t = line.split()
        out.setdefault(t[0].replace("rays A+RR", "rays_A+RR"), []).append([float(v) for v in t[1:5]])
    return {k: np.array(sorted(v)) for k, v in out.items()}


def read_gamma_obs(path):
    rows = [l.split()[:4] for l in open(path) if l.strip() and not l.startswith("#")]
    return np.array(rows, dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", default=os.path.join(DATA, "history.txt"))
    a = ap.parse_args()
    hist = read_history(a.history)
    gobs = read_gamma_obs(os.path.join(DATA, "gamma_obs.txt"))
    head, dp, below = fig_pk.read_pdf(os.path.join(DATA, "pdf_gamma.txt"))[-1]
    zpdf = float(head.split("z = ")[1].split()[0].rstrip(";"))

    plt.rcParams.update({"font.size": 9, "axes.labelsize": 10, "xtick.labelsize": 8.5,
                         "ytick.labelsize": 8.5, "axes.linewidth": 0.8, "axes.edgecolor": fig_pk.INK2})
    fig, (a0, a1, a2) = plt.subplots(1, 3, figsize=(7.2, 2.7))
    handles = {}
    for key, label, c, ls, lw in fig_pk.RUNS:
        if key in hist:
            h = hist[key]
            ln, = a0.plot(h[:, 0], h[:, 1], color=c, ls=ls, lw=lw)
            a0.plot(h[:, 0], h[:, 2], color=c, ls=ls, lw=lw * 0.6, alpha=0.6)
            ion = h[:, 3] > 0
            a1.plot(h[ion, 0], h[ion, 3] / 1e-12, color=c, ls=ls, lw=lw)
            handles[label] = ln
        if key in dp:
            ln, = a2.plot(*dp[key], color=c, ls=ls, lw=lw)
            handles.setdefault(label, ln)
    a1.errorbar(gobs[:, 0], gobs[:, 1], yerr=[gobs[:, 3], gobs[:, 2]], fmt="s", ms=3.5, color=OBS,
                mfc="white", ecolor=OBS, elinewidth=0.8, capsize=2, zorder=5, label="Gaikwad et al. 2023")
    a0.plot([], [], color=fig_pk.INK2, lw=1.4, label=r"$x_{\rm HII,V}$")
    a0.plot([], [], color=fig_pk.INK2, lw=0.9, alpha=0.6, label=r"$x_{\rm HII,M}$")
    a0.legend(fontsize=7.5, frameon=False, loc="lower left")
    a1.legend(fontsize=7.5, frameon=False, loc="lower right")

    zlo = min(h[:, 0].min() for h in hist.values())
    zhi = max(h[:, 0].max() for h in hist.values())
    for ax in (a0, a1):
        ax.set_xlim(max(zlo, 4.9), min(zhi, 9.0))
        ax.invert_xaxis()
        ax.set_xlabel(r"$z$")
    a0.set_ylim(0, 1.02)
    a0.set_ylabel(r"ionized fraction")
    a1.set_yscale("log")
    a1.set_ylabel(r"median $\Gamma_{\rm HI}$ [$10^{-12}$ s$^{-1}$]")
    a2.set_yscale("log")
    a2.set_ylim(1e-3, 20)
    a2.set_xlim(-1.2, 1.2)
    a2.set_xticks([-1, -0.5, 0, 0.5, 1])
    a2.set_xticklabels(["-1", "", "0", "", "1"])
    a2.set_xlabel(r"$\log_{10}(\Gamma_{\rm HI}/\langle\Gamma_{\rm HI}\rangle_V)$")
    a2.set_ylabel(r"$dP/d\log_{10}\Gamma_{\rm HI}$")
    a2.set_title(f"$z={zpdf:.2f}$", fontsize=9)
    for ax in (a0, a1, a2):
        ax.grid(alpha=0.3, lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    order = [lab for _, lab, *_ in fig_pk.RUNS if lab in handles]
    fig.legend([handles[l] for l in order], order, loc="upper center", ncol=min(len(order), 7),
               frameon=False, fontsize=8, handlelength=2.6, columnspacing=1.0, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = os.path.join(FIG, "fig_history")
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


if __name__ == "__main__":
    main()
