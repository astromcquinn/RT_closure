#!/usr/bin/env python3
"""The reionization history, the median photoionization rate and the mean
free path of every run.

  left:   the mass-weighted neutral fraction x_HI,M = 1 - x_HII,M against z
  middle: the median Gamma_HI of the ionised cells (x_HI < 1e-2) against z,
          with the measurements of Gaikwad et al. 2023 (data/gamma_obs.txt,
          squares)
  right:  lambda_mfp (912 A, pMpc) at the snapshots, as in fig_mfp_width.py
          (open symbols: the exponential fit), with Becker et al. 2021
          (squares) and Zhu et al. 2023 (diamonds)

Data: data/history.txt, one line per run and snapshot,
  label  z  xHII_V  xHII_M  GammaHI_ion_med[s^-1]
(labels as in data/pk_suite.txt: rays M1 OTVET split screen cone rays_A+RR;
'#' lines are comments), data/taueff_mfp_snap_A.txt ('#S' lines) and
data/lambda_mfp_obs.txt.

usage: python3 scripts/fig_history.py [--history PATH]
       (writes figures/fig_history.{pdf,png})
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import fig_mfp_width as fm  # noqa: E402  (the mean free path readers)
import fig_pk  # noqa: E402  (the paper's run colours)

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
    _, lam = fm.read_runs(os.path.join(DATA, "taueff_mfp_snap_A.txt"))
    lobs = fm.read_obs(os.path.join(DATA, "lambda_mfp_obs.txt"))

    plt.rcParams.update({"font.size": 9, "axes.labelsize": 10, "xtick.labelsize": 8.5,
                         "ytick.labelsize": 8.5, "axes.linewidth": 0.8, "axes.edgecolor": fig_pk.INK2})
    fig, (a0, a1, a2) = plt.subplots(1, 3, figsize=(7.2, 2.7))
    handles = {}
    for key, label, c, ls, lw in fig_pk.RUNS:
        if key == "split":  # not shown: similar to OTVET (said in the caption)
            continue
        if key in hist:
            h = hist[key]
            ln, = a0.plot(h[:, 0], 1 - h[:, 2], color=c, ls=ls, lw=lw)
            ion = h[:, 3] > 0
            a1.plot(h[ion, 0], h[ion, 3] / 1e-12, color=c, ls=ls, lw=lw)
            handles[label] = ln
        if key in lam:
            d = lam[key]
            ln, = a2.plot(d[:, 0], d[:, 1], color=c, ls=ls, lw=lw)
            fit = d[:, 2] > 0
            a2.plot(d[~fit, 0], d[~fit, 1], "o", color=c, ms=2.5)
            a2.plot(d[fit, 0], d[fit, 1], "o", color=c, ms=2.5, mfc="white")
            handles.setdefault(label, ln)
    for ref, mk in [("Becker21", "s"), ("Zhu23", "D")]:
        if ref in lobs:
            d = lobs[ref]
            a2.errorbar(d[:, 0], d[:, 1], yerr=[d[:, 3], d[:, 2]], fmt=mk, ms=3.5, color=OBS, mfc="white",
                        ecolor=OBS, elinewidth=0.8, capsize=2, zorder=5)
    a1.errorbar(gobs[:, 0], gobs[:, 1], yerr=[gobs[:, 3], gobs[:, 2]], fmt="s", ms=3.5, color=OBS,
                mfc="white", ecolor=OBS, elinewidth=0.8, capsize=2, zorder=5)

    zlo = min(h[:, 0].min() for h in hist.values())
    zhi = max(h[:, 0].max() for h in hist.values())
    for ax in (a0, a1, a2):
        ax.set_xlim(max(zlo, 4.9), min(zhi, 9.0))
        ax.invert_xaxis()
        ax.set_xlabel(r"$z$")
    a0.set_yscale("log")
    a0.set_ylabel(r"$x_{\rm HI,M}$")
    a1.set_yscale("log")
    a1.set_ylabel(r"median $\Gamma_{\rm HI}$ [$10^{-12}$ s$^{-1}$]")
    fm.log_axis(a2, [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30])
    a2.set_ylabel(r"$\lambda_{\rm mfp}$ (912 Å) [pMpc]")
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
