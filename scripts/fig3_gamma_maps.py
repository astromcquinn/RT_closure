#!/usr/bin/env python3
"""Figure 3: Gamma_HI maps, recomposed with labels at the printed size.

The panels are cut from NewRadHydroCode docs/figures/rt_suite_512_maps_gamma.png
(rt_suite_figures.py on the 512^3 suite: gammaHI_avg in 8-cell slabs through the
box middle; rows x_V = 0.49, 0.79, 0.97, 1.0; columns rays, M1, OTVET, split,
screen, cone, rays A+RR; log Gamma from 1e-14 to 1e-11 s^-1, magma). The
x_V = 0.49 row is left out (user, 2026-11-06). The final figure is to be drawn
from the cubes (rt_suite_figures.py --xv-gamma 0.8,0.97,1.0).

usage: python3 scripts/fig3_gamma_maps.py PATH/rt_suite_512_maps_gamma.png
       (writes figures/fig3_gamma_maps.png)
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.cm import ScalarMappable  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402
from PIL import Image  # noqa: E402

# pixel boxes of the source figure (2920 x 1660), found from its frames
ROWS = [((480, 841), "$z=6.20$\n$x_V=0.79$"), ((868, 1230), "$z=5.70$\n$x_V=0.97$"),
        ((1257, 1619), "$z=4.99$\n$x_V=1.00$")]
COLS = [((115, 477), "rays"), ((483, 845), "M1"), ((852, 1214), "OTVET"), ((1221, 1583), "split"),
        ((1589, 1951), "screen"), ((1958, 2320), "cone"), ((2327, 2688), "rays\ncase A + RR")]


def main():
    im = np.asarray(Image.open(sys.argv[1]).convert("RGB"))
    if im.shape[:2] != (1660, 2920):
        sys.exit(f"unexpected size {im.shape[:2]}; re-measure the panel boxes")
    nr, nc = len(ROWS), len(COLS)
    W = 6.5
    left, right, top, bottom, gap = 0.075, 0.855, 0.86, 0.01, 0.004
    w = (right - left - gap * (nc - 1)) / nc
    H = (w * W * nr + gap * W * (nr - 1)) / (top - bottom)
    h = w * W / H
    fig = plt.figure(figsize=(W, H))
    for i, ((y0, y1), rlab) in enumerate(ROWS):
        for j, ((x0, x1), clab) in enumerate(COLS):
            ax = fig.add_axes([left + j * (w + gap), top - (i + 1) * h - i * gap * W / H, w, h])
            ax.imshow(im[y0 + 2:y1 - 2, x0 + 2:x1 - 2], interpolation="none")
            ax.set_xticks([])
            ax.set_yticks([])
            if i == 0:
                ax.set_title(clab, fontsize=9)
            if j == 0:
                ax.set_ylabel(rlab, fontsize=9)
    cax = fig.add_axes([right + 0.015, bottom + 0.05, 0.018, top - bottom - 0.1])
    cb = fig.colorbar(ScalarMappable(norm=LogNorm(1e-14, 1e-11), cmap="magma"), cax=cax)
    cb.set_label(r"$\Gamma_{\rm HI}$ [s$^{-1}$]", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "fig3_gamma_maps.png")
    fig.savefig(out, dpi=400)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
