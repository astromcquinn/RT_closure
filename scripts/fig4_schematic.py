#!/usr/bin/env python3
"""Figure 4: schematic of the new closures.

(a) the direct + diffuse split: the thin minimum-image sum gives the
    optically thin light N_OT with its tensor h; the solution's photons beyond it
    are treated as isotropic.
(b) the cone tensor: receivers send HEALPix cones that march through
    mip-maps of the emissivity and the HI column; a thin near field inside
    r_c; attenuation behind neutral gas; the budget cutoff exp(-s/lambda_x).

usage: python3 scripts/fig4_schematic.py   (writes figures/fig4_schematic.{pdf,png})

Colours: the validated categorical slots 1-3 of the dataviz reference
palette (blue = diffuse light, orange = direct light, aqua = the near
field), every element labelled directly; text in ink.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Rectangle, Wedge  # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, HI = "#0b0b0b", "#52514e", "#6b6a66"

plt.rcParams.update({
    "font.size": 8, "mathtext.fontset": "cm", "axes.linewidth": 0.8,
    "text.color": INK, "axes.edgecolor": INK2,
})


def star(ax, x, y, s=70, c=INK, alpha=1.0, z=6):
    ax.scatter([x], [y], marker="*", s=s, color=c, alpha=alpha, zorder=z, linewidths=0)


def arrow(ax, p, q, c, lw=1.2, ls="-", alpha=1.0, shrink=6, z=4):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=7, color=c, lw=lw,
                                 linestyle=ls, alpha=alpha, shrinkA=shrink, shrinkB=shrink, zorder=z))


def panel_split(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(a) direct + diffuse split", loc="left", fontsize=9, color=INK)

    rx, ry = 5.0, 4.9
    # the minimum-image cube around the receiving cell
    ax.add_patch(Rectangle((2.5, 2.6), 5.0, 5.0, fill=False, ls=(0, (4, 3)), lw=0.9, ec=INK2))
    ax.text(2.55, 7.72, r"minimum image: sources within $L/2$", color=INK2, fontsize=7)
    # direct light of the current sources (thin sum, unattenuated)
    for sx, sy in [(3.2, 6.8), (6.9, 6.3), (3.6, 3.2), (6.6, 3.3)]:
        star(ax, sx, sy)
        arrow(ax, (sx, sy), (rx, ry), ORANGE, lw=1.4)
    ax.text(5.0, 7.15, r"optically thin: $N_{\rm OT}=q\,{\rm tr}\,\mathsf{S}/4\pi$, direction $\mathsf{h}$",
            color=INK, fontsize=7, ha="center", va="bottom")
    ax.text(3.3, 4.6, "diffuse", color=INK, fontsize=7, ha="right", va="center")
    # diffuse light: periodic images, old photons, recombination radiation
    for sx, sy in [(0.8, 8.0), (9.2, 8.0), (9.3, 2.6), (9.5, 5.1), (0.6, 5.3)]:
        star(ax, sx, sy, c=INK2, alpha=0.45)
    for a in np.deg2rad(np.arange(0, 360, 45) + 22.5):
        p = (rx + 1.35 * np.cos(a), ry + 1.35 * np.sin(a))
        arrow(ax, p, (rx + 0.35 * np.cos(a), ry + 0.35 * np.sin(a)), BLUE, lw=1.0, shrink=0)
    ax.text(0.15, 2.25, "diffuse: images and sources beyond $L/2$, older photons, recombinations",
            color=INK2, fontsize=6.5, ha="left", va="top")
    ax.add_patch(Rectangle((rx - 0.18, ry - 0.18), 0.36, 0.36, fc="white", ec=INK, lw=1.0, zorder=7))
    ax.annotate("cell", xy=(rx + 0.2, ry), xytext=(6.45, ry), fontsize=7, ha="left", va="center", color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6), zorder=8)

    # the photon budget of the cell
    y0, h = 0.45, 0.38
    ax.add_patch(Rectangle((1.0, y0), 3.6, h, fc=ORANGE, ec="white", lw=1.5))
    ax.add_patch(Rectangle((4.6, y0), 4.4, h, fc=BLUE, ec="white", lw=1.5))
    ax.text(2.8, y0 - 0.12, r"$\min(N, N_{\rm OT})$: $\mathsf{h}$", ha="center", va="top", fontsize=7)
    ax.text(6.8, y0 - 0.12, r"$N - N_{\rm OT}$: isotropic $\mathsf{I}/3$", ha="center", va="top", fontsize=7)
    ax.text(1.0, y0 + h + 0.12, r"the cell's photons $N$ (after overlap, $N > N_{\rm OT}$)", fontsize=7,
            va="bottom", color=INK)
    ax.text(5.0, 8.75, r"$\mathsf{P} = N\,\frac{\mathsf{I}}{3} + \min(N, N_{\rm OT})\,(\mathsf{h} - \frac{\mathsf{I}}{3})$",
            ha="center", fontsize=9)


def panel_cone(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(b) HI-attenuated cone tensor", loc="left", fontsize=9, color=INK)

    rx, ry, rc = 1.9, 4.5, 0.8
    half = 8.0  # half-opening, degrees (nside 4)
    smax = 8.4
    lamx = 5.0  # the budget cutoff length in this drawing
    island = Ellipse((5.6, 5.55), 1.2, 0.8, angle=16, fc=HI, ec="none", alpha=0.9, zorder=3)
    s_island = 3.3  # where the +16 deg cone enters the island

    for ang in [-32, -16, 0, 16, 32]:
        n = 36
        edges = rc * (smax / rc) ** (np.arange(n + 1) / n)
        for i in range(n):
            s0, s1 = edges[i], edges[i + 1]
            sm = 0.5 * (s0 + s1)
            t = np.exp(-sm / lamx)
            if ang == 16 and sm > s_island:
                t *= 0.12  # behind the neutral island
            ax.add_patch(Wedge((rx, ry), s1, ang - half, ang + half, width=s1 - s0, fc=ORANGE,
                               ec="none", alpha=0.08 + 0.42 * t, zorder=1))
        for sgn in (-1, 1):
            a = np.deg2rad(ang + sgn * half)
            ax.plot([rx + rc * np.cos(a), rx + smax * np.cos(a)], [ry + rc * np.sin(a), ry + smax * np.sin(a)],
                    color=ORANGE, lw=0.5, alpha=0.6, zorder=2)

    ax.add_patch(island)
    ax.text(5.6, 5.55, "neutral\nisland", ha="center", va="center", fontsize=6.5, color="white", zorder=4)
    ax.annotate("shadow: a hidden source", xy=(8.35, 6.55), xytext=(9.9, 8.05), fontsize=7, color=INK, ha="right",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.text(4.3, 6.75, r"$T=\sum_g W_g\,e^{-\sigma_g\,{\rm col}}$", fontsize=7.5, ha="left", color=INK, zorder=6)

    # samples along the central cone: a mip level matched to the cone width
    tan = np.tan(np.deg2rad(half))
    s = 1.05
    while s < smax - 0.6:
        d = max(2 * s * tan, 0.12)
        ax.add_patch(Circle((rx + s, ry), d / 2, fill=False, ec=INK2, lw=0.6, zorder=5))
        s += 0.5 * d * 2.2  # steps drawn wider than the real half-width, for legibility
    ax.annotate("samples: mip level\n" + r"$\propto$ cone width", xy=(rx + 4.3, ry - 0.42), xytext=(5.3, 2.05),
                fontsize=6.5, color=INK, ha="left",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))

    # sources
    for sx, sy in [(4.0, 4.65), (6.9, 4.25), (8.2, 6.4), (4.8, 2.75), (8.6, 3.1)]:
        star(ax, sx, sy)

    # near field and hand-over
    ax.add_patch(Circle((rx, ry), rc, fill=False, ec=AQUA, lw=1.2, zorder=5))
    ax.add_patch(Circle((rx, ry), 2 * rc, fill=False, ec=AQUA, lw=0.9, ls=(0, (3, 2)), zorder=5))
    ax.text(0.05, ry + 1.95, "near field $r<r_c$: thin FFT,\nhanded over to the cones by $2r_c$",
            fontsize=6.5, color=INK, va="bottom")
    ax.add_patch(Rectangle((rx - 0.16, ry - 0.16), 0.32, 0.32, fc="white", ec=INK, lw=1.0, zorder=7))
    ax.text(rx, ry - 0.95, "receiver\n(every 4 cells,\n192 cones)", ha="center", va="top", fontsize=6.5,
            color=INK)

    ax.text(9.9, 0.55, r"cones fade by the budget cutoff $e^{-s/\lambda_x}$" + "\n" + r"and continue through periodic images to $8L$",
            ha="right", va="center", fontsize=6.5, color=INK)
    ax.text(5.0, 8.75, r"$\mathsf{h} = \mathsf{h}_s + G_\sigma * (\mathsf{h}_{\rm cone} - \mathsf{h}_s)$",
            ha="center", fontsize=9)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "figures", "fig4_schematic")
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.55))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01, wspace=0.04)
    panel_split(axs[0])
    panel_cone(axs[1])
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=200)
    print("wrote", out + ".{pdf,png}")


if __name__ == "__main__":
    main()
