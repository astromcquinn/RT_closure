#!/usr/bin/env python3
"""Coherent and noise parts of the rays' transfer function in the uniform mean
free path test (appendix of main.tex).

usage: ray_noise.py
reads data/convergence/T_rays_N<N>_l<frac>.txt (T and the correlation r with
the sources, tools/analysis/moment_transfer.py of NewRadHydroCode) and
data/convergence/rays_pool.txt (live rays per cell at the end of each run),
prints, per run: the coherent part r T against arctan(k lam)/(k lam), the
part uncorrelated with the sources T sqrt(1 - r^2), and the rms per cell
sigma it corresponds to if white: the sources are nsrc = N^3/512 random
cells, P_L / Lbar^2 = 512 cells, so sigma = sqrt(512) T sqrt(1 - r^2).
"""
import os
import re

import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(here, "..", "data", "convergence")
SRC = 512.0  # cells per source


def load(N, frac):
    f = os.path.join(D, "T_rays_N%d_l%d.txt" % (N, frac))
    hdr = [ln for ln in open(f) if ln.startswith("# k*lam")][0]
    names = re.split(r"\s{2,}", hdr[2:].strip())
    a = np.array([[float(x) for x in ln.replace("(", " ").replace(")", " ").split()]
                  for ln in open(f) if not ln.startswith("#")])
    d = {n: a[:, i] for i, n in enumerate(names[:8])}
    for j, n in enumerate(names[8:]):
        n = re.sub(r"_N\d+_l\d", "", n)
        d[n], d["r_" + n] = a[:, 8 + 2 * j], a[:, 9 + 2 * j]
    return d


pool = {ln.split()[0]: float(ln.split()[1]) for ln in open(os.path.join(D, "rays_pool.txt"))}
for N, frac in ((128, 4), (128, 1), (64, 4), (64, 1)):
    d = load(N, frac)
    ex = d["exact"]
    print("N = %d, lambda = L/%d (%d cells)" % (N, frac, N // frac))
    for key in d:
        if not key.startswith("rays_f") or key.endswith("_avg"):
            continue
        nray = pool["rays_N%d_l%d_%s" % (N, frac, key[5:])]
        for tag in ("", "_avg"):
            T, r = d[key + tag], d["r_" + key + tag]
            coh = r * T / ex
            hi = slice(-4, None)  # the four highest k bins
            noise = T * np.sqrt(np.clip(1 - r * r, 0, None))
            sig = np.sqrt(SRC) * noise[hi].mean()
            print("  %-12s n_ray %5.1f  r T / exact: %.3f .. %.3f (all bins), %.3f at Nyquist;  T / exact at Nyquist %.2f;"
                  "  noise T (4 highest bins) %.4f %.4f %.4f %.4f -> sigma %.3f, sigma sqrt(n_ray) %.2f"
                  % (key[5:] + tag, nray, coh.min(), coh.max(), coh[-1], T[-1] / ex[-1], *noise[hi], sig, sig * np.sqrt(nray)))
