#!/usr/bin/env python3
"""Figures 2 and 4: power spectra, the ratio to the rays and r(k) with the rays.

  fig2: x_HII at every step of data/pk_xHII_21cmfast.txt (NewRadHydroCode
        excursion_set.py figure: every run and 21cmFAST), titled by the
        rays' z and x_V; the split is left out (it equals OTVET to < 1 % in
        power and 0.001 in r(k) at these epochs)
  fig4: delta_Gamma (gammaHI_avg) at the 'gamma' panels of data/pk_suite.txt
        (rt_suite_figures.py; x_V ~ 0.5, 0.8, 0.97 and after overlap); the
        PDFs of data/pdf_gamma.txt are read only to check the snapshots (the
        z = 4.99 PDF is drawn by fig_history.py)

Both figures stop at k = KMAX = 10 h/Mpc (user, 2026-11-28); --kmax 0 draws every
k of the data files (to the Nyquist frequency, 40 h/Mpc, and beyond).

usage: python3 scripts/fig_pk.py   (writes figures/fig2_pk_xHII.{pdf,png} and
       figures/fig4_pk_gamma.{pdf,png})
       python3 scripts/fig_pk.py --only xhii --xhii-data data/pk_xHII_21cmfast_early.txt \
               --xhii-out fig2_pk_xHII_early [--ratio-ylim 0.1,10]   (another set of epochs)
"""
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")

# the paper's runs: key in the data, label, colour, line style, width
# The methods' names are capitalised in the labels, as in the text (user, 2026-11-28).
RUNS = [("rays", "Rays", "#000000", "-", 2.2),
        ("M1", "M1", "#2a78d6", "-", 1.5),
        ("OTVET", "OTVET", "#eb6834", "-", 2.6),  # wide: the split (dashed, on top) follows it before overlap
        ("OTVET_nobg", "OTVET, no background", "#eb6834", (0, (4, 1.5)), 1.0),
        ("screen", "Screen", "#eda100", "-.", 1.5),
        ("cone", "Cone", "#e87ba4", ":", 2.0),
        ("rays_A+RR", "Rays, case A + RR", "#008300", "-", 1.2),
        ("21cmFAST", "21cmFAST", "#6250d6", "-", 1.8)]
INK2 = "#52514e"
KMAX = 10.0  # h/Mpc: the largest k drawn (0: all)


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


def read_xv(path):
    """step -> the reference run's (first column's) volume-weighted x_HII."""
    out, on = {}, False
    for line in open(path):
        if line.startswith("#"):
            on = line.startswith("# volume-weighted x_HII")
        elif on and line.strip():
            t = line.split()
            out[int(t[0])] = float(t[2])
    return out


def read_pdf(path):
    """[(header, {run: (x, dP/dlog10)}, {run: fraction below the first bin})] per panel."""
    out, cur, runs, rows, below = [], None, None, [], None

    def close():
        if cur is not None and rows:
            a = np.array(rows, dtype=float)
            out.append((cur, {r: (a[:, 0], a[:, 1 + i]) for i, r in enumerate(runs)},
                        dict(zip(runs, below))))

    for line in open(path):
        line = line.rstrip("\n").replace("rays A+RR", "rays_A+RR")
        if line.startswith("# gamma: panel"):
            close()
            cur, rows = line, []
        elif line.startswith("# runs:"):
            runs = line.split(":", 1)[1].split()
        elif line.startswith("# fraction below"):
            below = [float(v) for v in line.split(":", 1)[1].split()]
        elif line.strip() and not line.startswith("#") and cur is not None:
            rows.append(line.split())
    close()
    return out


def plain_log_labels(ax):
    """Label a log y axis with plain numbers (0.01, 0.1, 1). An axis that spans less than
    1.6 decades, as the spectra do below KMAX, also gets labels at 2 and 5 times the
    decades; the default there is '2 x 10^-1', which runs into the next panel."""
    lo, hi = ax.get_ylim()
    fmt = FuncFormatter(lambda y, _: f"{y:g}")
    ax.yaxis.set_major_formatter(fmt)
    if np.log10(hi / lo) < 1.6:
        ax.yaxis.set_minor_locator(LogLocator(subs=[2, 5]))
        ax.yaxis.set_minor_formatter(fmt)
    else:
        ax.yaxis.set_minor_formatter(NullFormatter())


def panel_grid(blocks, titles, ylabel, out, ylim_ratio=(0.3, 3), pdfs=None, skip=(), kmax=KMAX):
    """ylim_ratio: one (lo, hi) for every panel, or a list with one per panel.
    skip: run keys left out of the figure.
    kmax: the bins above it are not drawn, so that the axes scale to what is shown (0: all).
    pdfs: optional read_pdf() panels, one per block, drawn in a fourth row."""
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 10, "xtick.labelsize": 8.5,
                         "ytick.labelsize": 8.5, "axes.linewidth": 0.8, "axes.edgecolor": INK2})
    n = len(blocks)
    hr = [1.3, 1, 1] + ([0.42, 1.2] if pdfs else [])
    fig = plt.figure(figsize=(6.5, 6.2 + (2.3 if pdfs else 0)))
    gs = fig.add_gridspec(len(hr), n, height_ratios=hr, hspace=0.08,
                          wspace=0.36 if n > 3 else 0.3)
    axs = np.empty((3, n), dtype=object)
    for j in range(n):
        for i in range(3):
            axs[i, j] = fig.add_subplot(gs[i, j], sharex=axs[0, j] if i else None)
            if i < 2:
                axs[i, j].tick_params(labelbottom=False)
    handles = {}
    for j, ((runs, k, d), title) in enumerate(zip(blocks, titles)):
        a0, a1, a2 = axs[0, j], axs[1, j], axs[2, j]
        sel = k <= kmax * (1 + 1e-6) if kmax > 0 else np.ones(len(k), dtype=bool)
        k = k[sel]
        for key, label, c, ls, lw in RUNS:
            if key not in d or key in skip:
                continue
            D2, ratio, r = (v[sel] for v in d[key])
            h, = a0.plot(k, D2, color=c, ls=ls, lw=lw)
            a1.plot(k, ratio, color=c, ls=ls, lw=lw)
            a2.plot(k, r, color=c, ls=ls, lw=lw)
            handles[label] = h
        a0.set_title(title.replace(", ", "\n") if n > 3 else title, fontsize=9.5)
        a0.set_yscale("log")
        a1.set_yscale("log")
        lim = ylim_ratio[j] if isinstance(ylim_ratio, list) else ylim_ratio
        a1.set_ylim(*lim)
        if lim == (0.3, 3):
            a1.set_yticks([0.3, 0.5, 1, 2, 3])
            a1.set_yticklabels(["0.3", "0.5", "1", "2", "3"])
            a1.minorticks_off()
        else:
            plain_log_labels(a1)
        a1.axhline(1, color="#9a9a96", lw=0.8, zorder=0)
        plain_log_labels(a0)
        a2.set_ylim(0, 1.05)
        a2.set_yticks([0, 0.5, 1])
        for ax in (a0, a1, a2):
            ax.set_xscale("log")
            ax.grid(alpha=0.3, lw=0.5)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        if kmax > 0:
            a2.set_xlim(right=kmax)
        a2.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
        a2.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]")
        if j == 0:
            a0.set_ylabel(ylabel)
            a1.set_ylabel(r"$P/P_{\rm Rays}$")
            a2.set_ylabel(r"$r(k)$ with Rays")
        if pdfs:
            a3 = fig.add_subplot(gs[4, j], sharey=None)
            _, dp, below = pdfs[j]
            for key, label, c, ls, lw in RUNS:
                if key in dp:
                    a3.plot(*dp[key], color=c, ls=ls, lw=lw)
            a3.set_yscale("log")
            a3.set_ylim(1e-3, 20)
            if max(below.values()) > 0.005:
                a3.set_xlim(-3, 1.5)
                a3.set_xticks([-3, -2, -1, 0, 1])
            else:   # after overlap: no neutral cells, a narrow distribution
                a3.set_xlim(-1.2, 1.2)
                a3.set_xticks([-1, -0.5, 0, 0.5, 1])
                a3.set_xticklabels(["-1", "", "0", "", "1"])
            a3.grid(alpha=0.3, lw=0.5)
            a3.spines["top"].set_visible(False)
            a3.spines["right"].set_visible(False)
            a3.set_xlabel(r"$\log_{10}(\Gamma/\langle\Gamma\rangle_V)$")
            if j == 0:
                a3.set_ylabel(r"$dP/d\log_{10}\Gamma$")
            if "rays" in below and below["rays"] > 0.005:
                a3.text(0.03, 0.95, f"Rays: {below['rays']:.0%}\n" + r"below $10^{-4}$", transform=a3.transAxes,
                        ha="left", va="top", fontsize=7.5, color=INK2)
    order = [lab for _, lab, *_ in RUNS if lab in handles]
    fig.legend([handles[l] for l in order], order, loc="upper center", ncol=min(len(order), 4),
               frameon=False, fontsize=9, bbox_to_anchor=(0.5, 1.0), handlelength=2.8,
               columnspacing=1.2)
    top = 0.83 if n > 3 else 0.87
    if pdfs:
        top = 1 - (1 - top) * 6.2 / 8.5
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08 * 6.2 / (8.5 if pdfs else 6.2), top=top)
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--xhii-data", default=os.path.join(DATA, "pk_xHII_21cmfast.txt"),
                    help="the x_HII spectra (excursion_set.py figure output)")
    ap.add_argument("--xhii-out", default="fig2_pk_xHII", help="figure name under figures/")
    ap.add_argument("--ratio-ylim", default="0.3,3", help="the P/P_rays axis of the x_HII figure")
    ap.add_argument("--only", choices=("all", "xhii", "gamma"), default="all")
    ap.add_argument("--kmax", type=float, default=KMAX, help="largest k drawn, h/Mpc (0: all)")
    a = ap.parse_args()
    if a.only in ("all", "xhii"):
        lo, hi = (float(v) for v in a.ratio_ylim.split(","))
        fig_xhii(a.xhii_data, os.path.join(FIG, a.xhii_out), (lo, hi), a.kmax)
    if a.only in ("all", "gamma"):
        fig_gamma(a.kmax)


def fig_xhii(path, out, ylim_ratio, kmax=KMAX):
    bx = read_blocks(path)
    xv = read_xv(path)
    heads = {int(re.match(r"# step (\d+)", h).group(1)): h for h in bx}
    steps = sorted(heads)
    titles = [f"$z={float(re.search(r' z ([0-9.]+)', heads[s]).group(1)):.2f}$, $x_V={xv[s]:.2f}$"
              for s in steps]
    panel_grid([bx[heads[s]] for s in steps], titles,
               r"$\Delta^2_{x_{\rm HII}}(k)$", out, ylim_ratio=ylim_ratio,
               skip=("split",), kmax=kmax)  # the split = OTVET to < 1 % in power before overlap


def fig_gamma(kmax=KMAX):
    bs = read_blocks(os.path.join(DATA, "pk_suite.txt"))
    gam = [h for h in bs if h.startswith("# gamma")]
    titles = []
    for h in gam:
        m = re.search(r"x_V = ([\d.]+) z = ([\d.]+)", h)
        titles.append(f"$z={float(m.group(2)):.2f}$, $x_V={float(m.group(1)):.2f}$")
    pdfs = read_pdf(os.path.join(DATA, "pdf_gamma.txt"))
    zq = lambda h: float(re.search(r"z = ([\d.]+)", h).group(1))
    assert len(pdfs) == len(gam) and all(abs(zq(p[0]) - zq(h)) < 0.002 for p, h in zip(pdfs, gam)), \
        "the PDF panels are not the power-spectrum panels"
    # the PDF row was moved to fig_history.py (z = 4.99 only), 2026-11-18
    panel_grid([bs[h] for h in gam], titles, r"$\Delta^2_{\delta_\Gamma}(k)$",
               os.path.join(FIG, "fig4_pk_gamma"), ylim_ratio=[(0.3, 3)] * (len(gam) - 1) + [(0.02, 30)],
               kmax=kmax)


if __name__ == "__main__":
    main()
