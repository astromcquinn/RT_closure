#!/usr/bin/env python3
"""The distribution of tau_eff over 50 Mpc/h segments at each snapshot, for
every run: with the run's own Gamma_HI (top row) and with a uniform Gamma_HI
(bottom row; x_HI of the cells with x_HI < 1e-2 scaled to their median
Gamma), tau rescaled to Bosman et al. 2022's mean flux in both. The 84-16 %
widths are printed in each panel's corner for the rays and OTVET.

Data: data/taueff_pdf.txt and data/taueff_uniform.txt (made on klone by
$R/reion512late_figures/paper/taueff_pdf.py from the igm_stats.py --taueff
outputs). The moment runs' fourth snapshot is at z = 5.75, the rays' at 5.70.

usage: python3 scripts/fig_taueff_pdf.py   (writes figures/fig_taueff_pdf.{pdf,png})
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import fig_pk  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def read_pdf(path):
    out, cur = {}, None
    for line in open(path):
        t = line.split()
        if line.startswith("#P"):
            cur = out.setdefault((t[1], t[3]), {}).setdefault(float(t[2]), [])
        elif t and not line.startswith("#"):
            cur.append((float(t[0]), float(t[1])))
    return {k: {z: np.array(v) for z, v in d.items()} for k, d in out.items()}


def read_table(path):
    out = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        t = line.split()
        out.setdefault(t[0], []).append([float(v) for v in t[1:]])
    return {k: np.array(sorted(v)) for k, v in out.items()}


def main():
    pdf = read_pdf(os.path.join(DATA, "taueff_pdf.txt"))
    tab = read_table(os.path.join(DATA, "taueff_uniform.txt"))
    zs = sorted(pdf[("rays", "own")])
    plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.8, "axes.edgecolor": fig_pk.INK2})
    fig, axes = plt.subplots(2, len(zs), figsize=(7.2, 3.6), sharex="col", sharey="col")
    handles = {}
    for j, z in enumerate(zs):
        r = tab["rays"][j]
        lo, hi = max(0.0, r[1] - 1.6 * r[2]), r[1] + 2.6 * r[2]
        ymax = 0.0
        for i, (kind, wcol) in enumerate((("own", 2), ("uniform", 4))):
            ax = axes[i, j]
            for key, label, c, ls, lw in fig_pk.RUNS:
                if (key, kind) not in pdf:
                    continue
                d = pdf[(key, kind)]
                zk = min(d, key=lambda q: abs(q - z))
                handles[label], = ax.plot(d[zk][:, 0], d[zk][:, 1], color=c, ls=ls, lw=lw * 0.7)
                ymax = max(ymax, d[zk][:, 1].max())
            ax.set_xlim(lo, hi)
            ax.grid(alpha=0.3, lw=0.5)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.text(0.97, 0.95, "width\nrays %.2f\nOTVET %.2f" % (tab["rays"][j][wcol], tab["OTVET"][j][wcol]),
                    transform=ax.transAxes, ha="right", va="top", fontsize=6)
        axes[0, j].set_ylim(0, 1.08 * ymax)
        axes[0, j].set_title(f"$z={z:.2f}$", fontsize=8.5)
        axes[1, j].set_xlabel(r"$\tau_{\rm eff}$")
    axes[0, 0].set_ylabel(r"$dP/d\tau_{\rm eff}$, own $\Gamma_{\rm HI}$")
    axes[1, 0].set_ylabel(r"$dP/d\tau_{\rm eff}$, uniform $\Gamma_{\rm HI}$")
    order = [lab for _, lab, *_ in fig_pk.RUNS if lab in handles]
    fig.legend([handles[l] for l in order], order, loc="upper center", ncol=len(order), frameon=False,
               fontsize=7.5, handlelength=2.4, columnspacing=1.0, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(HERE, "..", "figures", "fig_taueff_pdf")
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


if __name__ == "__main__":
    main()
