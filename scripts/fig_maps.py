#!/usr/bin/env python3
"""Figures 1 and 3: slabs through the box middle, drawn from the cubes on klone.

Each panel is the mean of an 8-cell slab through the box middle (as
NewRadHydroCode rt_suite_figures.py does), at the reference (first) run's
snapshots STEPS. Every other column uses its snapshot nearest in z (the runs
write the same zdata1 redshifts; the moment runs' hydro steps can put one a
step earlier). A 21cmFAST column is an excursion_set.py run-mass output
directory (DIR/run/step_NNNN/fHI.bin), read like a run.

  --field xHII   (Fig. 1) 1 - fHI.bin, linear 0-1, cividis
  --field gamma  (Fig. 3) gammaHI_avg.bin (Gamma_HI averaged over the RT
                 substeps), log 1e-14 to 1e-11 s^-1, magma; cells below
                 1e-15 drawn at the bottom of the scale
  --field gamma --relative
                 Gamma over a reference value, in sharp bands at x1.25, 2
                 and 4 (blue below, red above, grey within +-25 %); slab
                 cells with x_HII < 0.5 (fHI.bin) black. The reference is
                 the median Gamma of the ionised cells (x_HII > 0.5) of the
                 whole box: of the first run's snapshot for every panel of a
                 row (--rel-to ref, the default), or of each panel's own run
                 (--rel-to own)

usage: fig_maps.py --field xHII --steps 69,84,93 --out figures/fig1_maps_xHII.png RUN:label ...
       fig_maps.py --field gamma --steps 84,93,99 --out figures/fig3_gamma_maps.png RUN:label ...
       fig_maps.py --field gamma --relative --steps 84,93,99 --out figures/fig3_gamma_maps.png RUN:label ...
       fig_maps.py ... --retitle OLD.png --out NEW.png x:label ...   (new labels on an existing figure,
                                                                     without the runs; see retitle())
A label may contain "\\n" for a two-line column title.
Writes <out>_panels.txt: which snapshot of which run went into each panel.
"""
import argparse
import glob
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.cm import ScalarMappable  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap, LogNorm, Normalize  # noqa: E402

FIELDS = {
    "xHII": dict(file="fHI.bin", f=lambda a: 1.0 - a, norm=Normalize(0, 1), cmap="cividis",
                 floor=None, label=r"$x_{\rm HII}$"),
    "gamma": dict(file="gammaHI_avg.bin", f=lambda a: a, norm=LogNorm(1e-14, 1e-11), cmap="magma",
                  floor=1e-15, label=r"$\Gamma_{\rm HI}$ [s$^{-1}$]"),
}


# --relative: band edges of Gamma / reference, their colours (blue below,
# grey around 1, red above) and the neutral cells' colour
REL_EDGES = [1 / 4, 1 / 2, 1 / 1.25, 1.25, 2, 4]
REL_LABELS = ["1/4", "1/2", "1/1.25", "1.25", "2", "4"]
REL_COLORS = ["#104281", "#3987e5", "#9ec5f4", "#f0efec", "#f2a3a2", "#e34948", "#9e2626"]
NEUTRAL = "#0b0b0b"


def rel_style():
    cmap = ListedColormap(REL_COLORS)
    cmap.set_bad(NEUTRAL)
    e = np.log10(REL_EDGES)
    return cmap, BoundaryNorm(np.r_[-30.0, e, 30.0], cmap.N)


def cube(d, fname):
    a = np.fromfile(os.path.join(d, fname), dtype=np.float32)
    N = round(a.size ** (1 / 3))
    return a.reshape(N, N, N)


def ion_median(d):
    """the median Gamma_HI of the cells with x_HII > 0.5 in the whole box"""
    g, fhi = cube(d, "gammaHI_avg.bin"), cube(d, "fHI.bin")
    return float(np.median(g[fhi < 0.5]))


def rel_slab(d, n, ref):
    """log10(slab-mean Gamma / ref), NaN where the slab-mean x_HII < 0.5"""
    g = slab(d, FIELDS["gamma"], n)
    x = slab(d, FIELDS["xHII"], n)
    with np.errstate(divide="ignore"):
        r = np.log10(np.maximum(g, 1e-30) / ref)
    return np.where(x < 0.5, np.nan, r)


def stats(d):
    out = {}
    for line in open(os.path.join(d, "stats.txt")):
        if " = " in line:
            k, v = line.split(" = ", 1)
            try:
                out[k.strip()] = float(v)
            except ValueError:
                pass
    return out


def snapshots(run, fname):
    """step -> (z, dir) of the snapshots with a non-empty FNAME cube."""
    rd = os.path.join(run, "run") if os.path.isdir(os.path.join(run, "run")) else run
    snaps = {}
    for d in sorted(glob.glob(os.path.join(rd, "step_[0-9][0-9][0-9][0-9]"))):
        f = os.path.join(d, fname)
        if os.path.exists(f) and os.path.getsize(f) > 0 and os.path.exists(os.path.join(d, "stats.txt")):
            snaps[int(d[-4:])] = (stats(d).get("redshift", np.nan), d)
    return snaps


def slab(d, fd, n):
    a = np.fromfile(os.path.join(d, fd["file"]), dtype=np.float32)
    N = round(a.size ** (1 / 3))
    a = fd["f"](a.reshape(N, N, N)[N // 2 - n // 2:N // 2 - n // 2 + n].astype(np.float64))
    m = a.mean(axis=0)
    return m if fd["floor"] is None else np.maximum(m, fd["floor"])


def layout(nr, nc, twoline):
    """The figure of nr x nc square panels: width and height [in], then left, right, gap,
    the panel's width and height, the vertical gap and the top of the first row (fractions)."""
    W = 7.2
    left, right, gap = 0.085, 0.885, 0.006
    head = 0.42 if twoline else 0.28                  # column titles [in]
    w = (right - left - gap * (nc - 1)) / nc          # panel width, fraction of W
    hin = w * W                                       # panel size [in]
    H = hin * nr + gap * W * (nr - 1) + head + 0.08
    h, gy, top = hin / H, gap * W / H, 1 - head / H
    return W, H, left, right, gap, w, h, gy, top


def colorbar(fig, a, fd, nr, right, h, gy, top):
    bot = top - nr * h - (nr - 1) * gy
    cax = fig.add_axes([right + 0.015, bot + 0.1 * (top - bot), 0.015, 0.8 * (top - bot)])
    if a.relative:
        cmap_r, norm_r = rel_style()
        cb = fig.colorbar(ScalarMappable(norm=norm_r, cmap=cmap_r), cax=cax, ticks=np.log10(REL_EDGES))
        cb.set_ticklabels(REL_LABELS)
        ref_lab = r"\bar\Gamma_{\rm Rays}" if a.rel_to == "ref" else r"\bar\Gamma"
        cb.set_label(rf"$\Gamma_{{\rm HI}}/{ref_lab}$ (black: neutral)", fontsize=8)
    else:
        cb = fig.colorbar(ScalarMappable(norm=fd["norm"], cmap=fd["cmap"]), cax=cax)
        cb.set_label(fd["label"], fontsize=8)
    cb.ax.tick_params(labelsize=7)
    return cb


def retitle(a, fd, specs, nr):
    """--retitle PNG: the column titles and the colour bar's label of an existing figure
    redrawn with the labels given now, every other pixel kept. The layout does not depend
    on the data, so the titles are drawn on empty panels of the same figure and the band
    above the first row (and the box of the colour bar's label) is copied into PNG's
    pixels. For a change of labels without the runs' cubes."""
    import matplotlib.image as mi
    old = mi.imread(a.retitle)
    nc = len(specs)
    W, H, left, right, gap, w, h, gy, top = layout(nr, nc, any("\n" in l for _, l in specs))
    fig = plt.figure(figsize=(W, H))
    for j, (_, lab) in enumerate(specs):
        ax = fig.add_axes([left + j * (w + gap), top - h, w, h])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(lab, fontsize=8)
    cb = colorbar(fig, a, fd, nr, right, h, gy, top)
    fig.set_dpi(300)
    fig.canvas.draw()
    new = np.asarray(fig.canvas.buffer_rgba()).astype(np.float32) / 255
    if new.shape[:2] != old.shape[:2]:
        raise SystemExit(f"{a.retitle} is {old.shape[:2]}, this layout {new.shape[:2]}: other labels, steps or runs?")
    out = old.copy()
    if out.shape[2] == 3:
        new = new[..., :3]
    ytop = int(np.floor((1 - top) * new.shape[0])) - 2        # the band above the first row
    out[:ytop] = new[:ytop]
    boxes = [f"rows 0-{ytop - 1}"]
    if a.relative:
        bb = cb.ax.yaxis.label.get_window_extent()
        x0, x1 = int(np.floor(bb.x0)) - 3, int(np.ceil(bb.x1)) + 3
        y0, y1 = new.shape[0] - int(np.ceil(bb.y1)) - 3, new.shape[0] - int(np.floor(bb.y0)) + 3
        out[y0:y1, x0:x1] = new[y0:y1, x0:x1]
        boxes.append(f"x {x0}-{x1}, y {y0}-{y1}")
    mi.imsave(a.out, out, dpi=300)
    print("retitled", a.retitle, "->", a.out, "; replaced", "; ".join(boxes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="RUN:label; the first is the reference")
    ap.add_argument("--field", choices=sorted(FIELDS), default="xHII")
    ap.add_argument("--steps", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--slab", type=int, default=8)
    ap.add_argument("--tol", type=float, default=0.06)
    ap.add_argument("--relative", action="store_true",
                    help="gamma only: Gamma over the median of the ionised cells, in bands")
    ap.add_argument("--rel-to", choices=("ref", "own"), default="ref",
                    help="--relative: the first run's median (ref) or each run's own (own)")
    ap.add_argument("--retitle", metavar="PNG",
                    help="redraw only the column titles and the colour bar's label of PNG (a figure "
                         "of this script with the same steps and runs) with the labels given now; "
                         "the runs are not read")
    a = ap.parse_args()
    if a.relative and a.field != "gamma":
        ap.error("--relative applies to --field gamma")
    fd = FIELDS[a.field]
    if a.relative:
        cmap_r, norm_r = rel_style()
    specs = [(r.partition(":")[0], (r.partition(":")[2] or os.path.basename(r)).replace("\\n", "\n"))
             for r in a.runs]
    steps = [int(s) for s in a.steps.split(",")]
    if a.retitle:
        return retitle(a, fd, specs, len(steps))
    snaps = [snapshots(p, fd["file"]) for p, _ in specs]
    nr, nc = len(steps), len(specs)
    W, H, left, right, gap, w, h, gy, top = layout(nr, nc, any("\n" in l for _, l in specs))
    fig = plt.figure(figsize=(W, H))
    log = []
    for i, st in enumerate(steps):
        z0, d0 = snaps[0][st]
        xv0 = None
        ref0 = ion_median(d0) if a.relative else None
        if a.relative:
            log.append(f"{st}: reference median Gamma of the ionised cells ({specs[0][1]!r}) = {ref0:.4e}")
        for j, ((p, lab), sn) in enumerate(zip(specs, snaps)):
            ax = fig.add_axes([left + j * (w + gap), top - (i + 1) * h - i * gy, w, h])
            ax.set_xticks([])
            ax.set_yticks([])
            s_ = min(sn, key=lambda s: abs(sn[s][0] - z0)) if sn else None
            if s_ is None or abs(sn[s_][0] - z0) > a.tol:
                ax.text(0.5, 0.5, "-", ha="center", va="center", transform=ax.transAxes)
                log.append(f"{st} {lab!r}: none within {a.tol} of z = {z0:.4f}")
                continue
            xv = float(stats(sn[s_][1]).get("xHII_V", np.nan))
            if j == 0:
                xv0 = xv
            line = f"{st} {lab!r}: {sn[s_][1]} z = {sn[s_][0]:.4f} xHII_V = {xv:.4f}"
            if a.relative:
                ref = ref0 if a.rel_to == "ref" else ion_median(sn[s_][1])
                if a.rel_to == "own":
                    line += f" median = {ref:.4e}"
                m = np.ma.masked_invalid(rel_slab(sn[s_][1], a.slab, ref))
                ax.imshow(m.T, origin="lower", norm=norm_r, cmap=cmap_r, interpolation="nearest")
            else:
                m = slab(sn[s_][1], fd, a.slab)
                ax.imshow(m.T, origin="lower", norm=fd["norm"], cmap=fd["cmap"], interpolation="nearest")
            log.append(line)
            if i == 0:
                ax.set_title(lab, fontsize=8)
            if j == 0:
                ax.set_ylabel(f"$z={z0:.2f}$\n$x_V={xv0:.2f}$", fontsize=8)
    colorbar(fig, a, fd, nr, right, h, gy, top)
    fig.savefig(a.out, dpi=300)
    with open(os.path.splitext(a.out)[0] + "_panels.txt", "w") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
