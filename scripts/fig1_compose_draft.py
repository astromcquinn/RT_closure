#!/usr/bin/env python3
"""Draft of Figure 1 cut from a rendered figure: the x_HII maps of the rays,
M1, thin OTVET, the cone and 21cmFAST (on the suite's own density,
R_max = 15 Mpc; mass-dependent sources with the suite's abundance-matched
slope, branch 21cmfast-mass-sources, 61b8312) at z = 6.97, 6.20 and 5.70.

The panels come from NewRadHydroCode's docs/figures/taueff_21cmfast_fig8_maps.png
(excursion_set.py figure --es rmax15: rows z = 6.97,
6.45, 6.20, 5.98, 5.70; columns rays, rays A+RR, M1, OTVET, split, screen,
cone, 21cmFAST; the 8-cell slab through the box middle, as in
rt_suite_figures.py). The final figure is to be drawn from the cubes on
klone (outline.md, Figure 1).

usage: python3 scripts/fig1_compose_draft.py PATH/taueff_21cmfast_fig8_maps.png
       (writes figures/fig1_maps_xHII_draft.png)
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.cm import ScalarMappable  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from PIL import Image  # noqa: E402

# pixel boxes of the source figure (3160 x 1960), found from its frames
ROWS = {6.97: (105, 447), 6.45: (471, 814), 6.20: (838, 1181), 5.98: (1205, 1547), 5.70: (1571, 1914)}
COLS = {"rays": (124, 467), "rays A+RR": (473, 816), "M1": (822, 1165), "OTVET": (1171, 1514),
        "split": (1520, 1863), "screen": (1869, 2211), "cone": (2218, 2560), "21cmFAST": (2566, 2909)}
XV = {6.97: 0.49, 6.45: 0.68, 6.20: 0.79, 5.98: 0.88, 5.70: 0.97}

PICK_ROWS = [6.97, 6.20, 5.70]
PICK_COLS = [("rays", "rays"), ("M1", "M1"), ("OTVET", "OTVET (thin)"), ("cone", "cone"),
             ("21cmFAST", "21cmFAST")]


def main():
    src = sys.argv[1]
    im = np.asarray(Image.open(src).convert("RGB"))
    if im.shape[:2] != (1960, 3160):
        sys.exit(f"{src}: unexpected size {im.shape[:2]}; re-measure the panel boxes")
    nr, nc = len(PICK_ROWS), len(PICK_COLS)
    fig = plt.figure(figsize=(7.2, 7.2 * nr / nc * 1.0 + 0.35))
    left, right, top, bottom, gap = 0.045, 0.885, 0.955, 0.01, 0.006
    w = (right - left - gap * (nc - 1)) / nc
    h = (top - bottom - gap * (nr - 1)) / nr
    for i, z in enumerate(PICK_ROWS):
        y0, y1 = ROWS[z]
        for j, (key, title) in enumerate(PICK_COLS):
            x0, x1 = COLS[key]
            tile = im[y0 + 2:y1 - 2, x0 + 2:x1 - 2]
            ax = fig.add_axes([left + j * (w + gap), top - (i + 1) * h - i * gap, w, h])
            ax.imshow(tile, interpolation="none")
            ax.set_xticks([])
            ax.set_yticks([])
            if i == 0:
                ax.set_title(title, fontsize=8)
            if j == 0:
                ax.set_ylabel(f"$z={z:.2f}$, $x_V={XV[z]:.2f}$", fontsize=8)
    cax = fig.add_axes([right + 0.015, bottom + 0.1 * (top - bottom), 0.015, 0.8 * (top - bottom)])
    cb = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap="cividis"), cax=cax)
    cb.set_label(r"$x_{\rm HII}$", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "fig1_maps_xHII_draft.png")
    fig.savefig(out, dpi=300)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
