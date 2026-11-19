#!/usr/bin/env python3
"""The temperature of the ionized gas (x_HI < 1e-2) at z = 4.99, after overlap,
in the runs of the late-end 512^3 suite.

  left:   the volume-weighted PDF of log10 T of the ionized cells
  middle: the same for the cells at the mean density (|log10 Delta| < 0.05)
  right:  the median T against Delta = rho_gas / mean (band: 16-84 % of the
          rays)

Data: data/temp_z5.txt, data/temp_z5_pdf.txt (made on klone by
$R/reion512late_figures/paper/temp_z5.py).

usage: python3 scripts/fig_temp_z5.py   (writes figures/fig_temp_z5.{pdf,png})
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
STYLE = [("rays", "rays", "#000000", "-", 2.0), ("M1", "M1", "#2a78d6", "-", 1.3),
         ("OTVET", "OTVET", "#eb6834", "-", 1.3), ("split", "split", "#e3a008", "--", 1.3),
         ("screen", "screen", "#a35bd3", "-.", 1.3), ("cone", "cone", "#1baf7a", "-", 1.3),
         ("rays_A+RR", "rays, case A + RR", "#6b6a66", ":", 1.6)]


def main():
    tab, pdf, cur = {}, {}, None
    for line in open(os.path.join(DATA, "temp_z5.txt")):
        t = line.split()
        if t and not line.startswith("#"):
            tab.setdefault(t[0], []).append([float(v) for v in t[1:]])
    for line in open(os.path.join(DATA, "temp_z5_pdf.txt")):
        t = line.split()
        if line.startswith("#P"):
            cur = pdf.setdefault(t[1], [])
        elif t and not line.startswith("#"):
            cur.append([float(v) for v in t])
    plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.8, "axes.edgecolor": "#52514e"})
    fig, (a0, a1, a2) = plt.subplots(1, 3, figsize=(7.2, 2.6))
    for key, label, c, ls, lw in STYLE:
        p, r = np.array(pdf[key]), np.array(tab[key])
        a0.plot(p[:, 0], p[:, 1], color=c, ls=ls, lw=lw, label=label)
        a1.plot(p[:, 0], p[:, 2], color=c, ls=ls, lw=lw)
        ok = r[:, 1] > 1000
        if key == "rays":
            a2.fill_between(r[ok, 0], r[ok, 2] / 1e4, r[ok, 4] / 1e4, color="#000000", alpha=0.12, lw=0)
        a2.plot(r[ok, 0], r[ok, 3] / 1e4, color=c, ls=ls, lw=lw, label=label)
    a0.set_xlim(3.6, 4.7)
    a1.set_xlim(3.6, 4.6)
    for ax, lab in ((a0, "all ionized gas"), (a1, r"$|\log_{10}\Delta|<0.05$")):
        ax.set_ylim(0, None)
        ax.set_xlabel(r"$\log_{10}(T/{\rm K})$")
        ax.set_ylabel(r"$dP/d\log_{10}T$")
        ax.set_title(lab, fontsize=8)
    a2.set_yscale("log")
    a2.set_ylim(0.25, 5)
    a2.set_yticks([0.5, 1, 2, 3, 5])
    a2.set_yticklabels(["0.5", "1", "2", "3", "5"])
    a2.minorticks_off()
    a2.set_xlabel(r"$\log_{10}\Delta$")
    a2.set_ylabel(r"median $T$ [$10^4$ K]")
    a2.set_title("$z=4.99$", fontsize=8)
    a2.legend(fontsize=6, frameon=False, loc="lower right", handlelength=2.6, labelspacing=0.25)
    for ax in (a0, a1, a2):
        ax.grid(alpha=0.3, lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = os.path.join(HERE, "..", "figures", "fig_temp_z5")
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


if __name__ == "__main__":
    main()
