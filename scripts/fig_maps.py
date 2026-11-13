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

usage: fig_maps.py --field xHII --steps 69,84,93 --out figures/fig1_maps_xHII.png RUN:label ...
       fig_maps.py --field gamma --steps 84,93,99 --out figures/fig3_gamma_maps.png RUN:label ...
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
from matplotlib.colors import LogNorm, Normalize  # noqa: E402

FIELDS = {
    "xHII": dict(file="fHI.bin", f=lambda a: 1.0 - a, norm=Normalize(0, 1), cmap="cividis",
                 floor=None, label=r"$x_{\rm HII}$"),
    "gamma": dict(file="gammaHI_avg.bin", f=lambda a: a, norm=LogNorm(1e-14, 1e-11), cmap="magma",
                  floor=1e-15, label=r"$\Gamma_{\rm HI}$ [s$^{-1}$]"),
}


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="RUN:label; the first is the reference")
    ap.add_argument("--field", choices=sorted(FIELDS), default="xHII")
    ap.add_argument("--steps", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--slab", type=int, default=8)
    ap.add_argument("--tol", type=float, default=0.06)
    a = ap.parse_args()
    fd = FIELDS[a.field]
    specs = [(r.partition(":")[0], (r.partition(":")[2] or os.path.basename(r)).replace("\\n", "\n"))
             for r in a.runs]
    steps = [int(s) for s in a.steps.split(",")]
    snaps = [snapshots(p, fd["file"]) for p, _ in specs]
    nr, nc = len(steps), len(specs)
    W = 7.2
    left, right, gap = 0.085, 0.885, 0.006
    head = 0.42 if any("\n" in l for _, l in specs) else 0.28   # column titles [in]
    w = (right - left - gap * (nc - 1)) / nc          # panel width, fraction of W
    hin = w * W                                       # panel size [in]
    H = hin * nr + gap * W * (nr - 1) + head + 0.08
    h, gy, top = hin / H, gap * W / H, 1 - head / H
    fig = plt.figure(figsize=(W, H))
    log = []
    for i, st in enumerate(steps):
        z0, d0 = snaps[0][st]
        xv0 = None
        for j, ((p, lab), sn) in enumerate(zip(specs, snaps)):
            ax = fig.add_axes([left + j * (w + gap), top - (i + 1) * h - i * gy, w, h])
            ax.set_xticks([])
            ax.set_yticks([])
            s_ = min(sn, key=lambda s: abs(sn[s][0] - z0)) if sn else None
            if s_ is None or abs(sn[s_][0] - z0) > a.tol:
                ax.text(0.5, 0.5, "-", ha="center", va="center", transform=ax.transAxes)
                log.append(f"{st} {lab!r}: none within {a.tol} of z = {z0:.4f}")
                continue
            m = slab(sn[s_][1], fd, a.slab)
            xv = float(stats(sn[s_][1]).get("xHII_V", np.nan))
            if j == 0:
                xv0 = xv
            log.append(f"{st} {lab!r}: {sn[s_][1]} z = {sn[s_][0]:.4f} xHII_V = {xv:.4f}")
            ax.imshow(m.T, origin="lower", norm=fd["norm"], cmap=fd["cmap"], interpolation="nearest")
            if i == 0:
                ax.set_title(lab, fontsize=8)
            if j == 0:
                ax.set_ylabel(f"$z={z0:.2f}$\n$x_V={xv0:.2f}$", fontsize=8)
    bot = top - nr * h - (nr - 1) * gy
    cax = fig.add_axes([right + 0.015, bot + 0.1 * (top - bot), 0.015, 0.8 * (top - bot)])
    cb = fig.colorbar(ScalarMappable(norm=fd["norm"], cmap=fd["cmap"]), cax=cax)
    cb.set_label(fd["label"], fontsize=8)
    cb.ax.tick_params(labelsize=7)
    fig.savefig(a.out, dpi=300)
    with open(os.path.splitext(a.out)[0] + "_panels.txt", "w") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
