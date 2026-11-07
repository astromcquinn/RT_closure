#!/usr/bin/env python3
"""Figures 2 and 4: power spectra, the ratio to the rays and r(k) with the rays.

  fig2: x_HII at z = 6.97, 6.20, 5.70 (x_V = 0.49, 0.79, 0.97 in the rays), every
        run and 21cmFAST (data/pk_xHII_21cmfast.txt, NewRadHydroCode
        excursion_set.py figure, branch 21cmfast-mass-sources)
  fig4: delta_Gamma (gammaHI_avg) at x_V = 0.49, 0.79, 0.97 and after overlap
        (z = 4.99), every run (data/pk_suite.txt, rt_suite_figures.py)

usage: python3 scripts/fig_pk.py   (writes figures/fig2_pk_xHII.{pdf,png} and
       figures/fig4_pk_gamma.{pdf,png})
"""
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")

# the paper's runs: key in the data, label, colour, line style, width
RUNS = [("rays", "rays", "#000000", "-", 2.2),
        ("M1", "M1", "#2a78d6", "-", 1.5),
        ("OTVET", "OTVET", "#eb6834", "-", 1.5),
        ("split", "split", "#1baf7a", "--", 1.5),
        ("screen", "screen", "#eda100", "-.", 1.5),
        ("cone", "cone", "#e87ba4", ":", 2.0),
        ("rays_A+RR", "rays, case A + RR", "#008300", "-", 1.2),
        ("21cmFAST", "21cmFAST", "#6250d6", "-", 1.8)]
INK2 = "#52514e"


def read_blocks(path):
    """{header line: (run names, k, {run: (Delta2, ratio, r)})}"""
    blocks, cur, runs, rows = {}, None, None, []

    def close():
        if cur is not None and rows:
            a = np.array(rows, dtype=float)
            blocks[cur] = (runs, a[:, 0], {r: (a[:, 1 + 3 * i], a[:, 2 + 3 * i], a[:, 3 + 3 * i])
                                           for i, r in enumerate(runs)})

    for line in open(path):
        line = line.rstrip("\n").replace("rays A+RR", "rays_A+RR")
        if line.startswith("# runs:"):
            runs = line.split(":", 1)[1].split()
        elif line.startswith("#"):
            if re.match(r"# (step \d+ z|xHII: panel|gamma: panel)", line):
                close()
                cur, rows = line, []
            else:
                close()
                cur, rows = None, []
        elif line.strip() and cur is not None:
            rows.append(line.split())
    close()
    return blocks


def panel_grid(blocks, titles, ylabel, out, ylim_ratio=(0.1, 10)):
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 10, "xtick.labelsize": 8.5,
                         "ytick.labelsize": 8.5, "axes.linewidth": 0.8, "axes.edgecolor": INK2})
    n = len(blocks)
    fig, axs = plt.subplots(3, n, figsize=(6.5, 6.2), sharex=True, squeeze=False,
                            gridspec_kw={"height_ratios": [1.3, 1, 1], "hspace": 0.08,
                                         "wspace": 0.36 if n > 3 else 0.3})
    handles = {}
    for j, ((runs, k, d), title) in enumerate(zip(blocks, titles)):
        a0, a1, a2 = axs[0, j], axs[1, j], axs[2, j]
        for key, label, c, ls, lw in RUNS:
            if key not in d:
                continue
            D2, ratio, r = d[key]
            h, = a0.plot(k, D2, color=c, ls=ls, lw=lw)
            a1.plot(k, ratio, color=c, ls=ls, lw=lw)
            a2.plot(k, r, color=c, ls=ls, lw=lw)
            handles[label] = h
        a0.set_title(title.replace(", ", "\n") if n > 3 else title, fontsize=9.5)
        a0.set_yscale("log")
        a1.set_yscale("log")
        a1.set_ylim(*ylim_ratio)
        a1.axhline(1, color="#9a9a96", lw=0.8, zorder=0)
        a2.set_ylim(0, 1.05)
        a2.set_yticks([0, 0.5, 1])
        for ax in (a0, a1, a2):
            ax.set_xscale("log")
            ax.grid(alpha=0.3, lw=0.5)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        a2.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]")
        if j == 0:
            a0.set_ylabel(ylabel)
            a1.set_ylabel(r"$P/P_{\rm rays}$")
            a2.set_ylabel(r"$r(k)$ with the rays")
    order = [lab for _, lab, *_ in RUNS if lab in handles]
    fig.legend([handles[l] for l in order], order, loc="upper center", ncol=min(len(order), 4),
               frameon=False, fontsize=9, bbox_to_anchor=(0.5, 1.0), handlelength=2.8,
               columnspacing=1.2)
    fig.subplots_adjust(left=0.1, right=0.99, bottom=0.08, top=0.87)
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


def main():
    bx = read_blocks(os.path.join(DATA, "pk_xHII_21cmfast.txt"))
    keys = {round(float(re.search(r" z ([\d.]+)", h).group(1)), 2): h for h in bx}
    xv = {6.97: 0.49, 6.2: 0.79, 5.7: 0.97}
    sel = [bx[keys[z]] for z in (6.97, 6.2, 5.7)]
    panel_grid(sel, [f"$z={z:.2f}$, $x_V={xv[z]:.2f}$" for z in (6.97, 6.20, 5.70)],
               r"$\Delta^2_{x_{\rm HII}}(k)$", os.path.join(FIG, "fig2_pk_xHII"))

    bs = read_blocks(os.path.join(DATA, "pk_suite.txt"))
    gam = [h for h in bs if h.startswith("# gamma")]
    titles = []
    for h in gam:
        m = re.search(r"x_V = ([\d.]+) z = ([\d.]+)", h)
        titles.append(f"$z={float(m.group(2)):.2f}$, $x_V={float(m.group(1)):.2f}$")
    panel_grid([bs[h] for h in gam], titles, r"$\Delta^2_{\delta_\Gamma}(k)$",
               os.path.join(FIG, "fig4_pk_gamma"), ylim_ratio=(0.02, 30))


if __name__ == "__main__":
    main()
