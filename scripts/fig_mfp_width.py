#!/usr/bin/env python3
"""The mean free path and the tau_eff scatter of every RT method, from the
full-box snapshots only.

(a) lambda_mfp (912 A, pMpc) at the snapshots: the distance at which the
    mean transmission from random starts falls to 1/e; at z ~ 5, where
    that exceeds the sightlines, the exponential fit from ionised starts
    (open symbols). The observed values of Becker et al. 2021 and Zhu et
    al. 2023 in grey.
(b) tau_eff(84 %) - tau_eff(16 %) over 50 Mpc/h segments (3 x 8192
    redshift-space skewers per snapshot; a box-length skewer joined to
    10 Mpc/h of another), with tau rescaled at each snapshot so that the
    mean flux equals Bosman et al. 2022's.

    The observed widths of Bosman et al. 2022 (Fig. A1, fixed 50 cMpc/h
    bins; data/taueff_width_obs.txt): non-detections at the detection limit,
    error bars the 16-84 % of a bootstrap over sightlines; where
    non-detections at tau = infinity widen it, a dotted line up to that
    width (an arrow where it is unbounded).

Data: data/taueff_mfp_snap_A.txt (NewRadHydroCode taueff_z.py --full --norm;
the '#S' lines give lambda_mfp and whether it is the fit),
data/lambda_mfp_obs.txt and data/taueff_width_obs.txt.

usage: python3 scripts/fig_mfp_width.py   (writes figures/fig_mfp_width.{pdf,png})
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# the paper's runs, colours and line styles (as rt_suite_figures.py)
RUNS = [("rays", "rays", "#000000", "-"),
        ("M1", "M1", "#2a78d6", "-"),
        ("OTVET", "OTVET", "#eb6834", "-"),
        ("split", "split", "#1baf7a", "--"),
        ("screen", "screen", "#eda100", "-."),
        ("cone", "cone", "#e87ba4", ":"),
        ("rays_A+RR", "rays, case A + RR", "#008300", "-")]
INK, INK2, OBS = "#0b0b0b", "#52514e", "#6b6a66"
ZMIN, ZMAX = 4.9, 6.3


def read_runs(path):
    width, lam = {}, {}
    for line in open(path):
        t = line.split()
        if not t:
            continue
        if t[0] == "#S":  # label z tau_eff lambda is_fit
            lam.setdefault(t[1], []).append((float(t[2]), float(t[4]), int(t[5])))
        elif not line.startswith("#"):  # label z tau16 tau50 tau84 width lambda
            width.setdefault(t[0], []).append((float(t[1]), float(t[5])))
    return ({k: np.array(sorted(v)) for k, v in width.items()},
            {k: np.array(sorted(v)) for k, v in lam.items()})


def read_obs(path):
    out = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        z, l, ep, em, ref = line.split()
        out.setdefault(ref, []).append((float(z), float(l), float(ep), float(em)))
    return {k: np.array(v) for k, v in out.items()}


def read_width_obs(path):
    """z, width (non-detections at the limit), its bootstrap 16/84 %, and the
    width with non-detections at infinity (inf: unbounded)"""
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        t = line.split()
        rows.append([float(t[0]), float(t[5]), float(t[6]), float(t[8]), float(t[9])])
    return np.array(rows)


def log_axis(ax, ticks):
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%g"))
    ax.yaxis.set_minor_formatter(NullFormatter())


def main():
    width, lam = read_runs(os.path.join(DATA, "taueff_mfp_snap_A.txt"))
    obs = read_obs(os.path.join(DATA, "lambda_mfp_obs.txt"))
    plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.8, "text.color": INK,
                         "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for key, label, c, ls in RUNS:
        lw = 2.0 if key == "rays" else 1.4
        if key in lam:
            d = lam[key]
            m = (d[:, 0] >= ZMIN) & (d[:, 0] <= ZMAX)
            d = d[m]
            a0.plot(d[:, 0], d[:, 1], color=c, ls=ls, lw=lw, label=label)
            fit = d[:, 2] > 0
            a0.plot(d[~fit, 0], d[~fit, 1], "o", color=c, ms=3.5)
            a0.plot(d[fit, 0], d[fit, 1], "o", color=c, ms=3.5, mfc="white")
        if key in width:
            d = width[key]
            a1.plot(d[:, 0], d[:, 1], color=c, ls=ls, lw=lw, marker="o", ms=3.5, label=label)
    for ref, mk, name in [("Becker21", "s", "Becker et al. 2021"), ("Zhu23", "D", "Zhu et al. 2023")]:
        if ref in obs:
            d = obs[ref]
            a0.errorbar(d[:, 0], d[:, 1], yerr=[d[:, 3], d[:, 2]], fmt=mk, ms=4, color=OBS, mfc="white",
                        ecolor=OBS, elinewidth=0.8, capsize=2, label=name)
    wo = read_width_obs(os.path.join(DATA, "taueff_width_obs.txt"))
    a1.errorbar(wo[:, 0], wo[:, 1], yerr=[wo[:, 1] - wo[:, 2], wo[:, 3] - wo[:, 1]], fmt="s", ms=4,
                color=OBS, mfc="white", ecolor=OBS, elinewidth=0.8, capsize=2, zorder=5,
                label="Bosman et al. 2022")
    for z, w0, _, _, w1 in wo:
        if w1 > w0 * 1.02:
            top = w1 if np.isfinite(w1) else 3.6
            a1.plot([z, z], [w0, top], ls=":", color=OBS, lw=0.9, zorder=4)
            a1.plot([z], [top], marker="^" if not np.isfinite(w1) else "_", color=OBS, ms=4, zorder=4)
    a0.plot([], [], "o", color=INK2, ms=3.5, mfc="white", label="exponential fit")
    log_axis(a0, [0.2, 0.5, 1, 2, 5, 10, 20, 50])
    a0.set_ylabel(r"$\lambda_{\rm mfp}$ (912 \AA) [pMpc]" if plt.rcParams["text.usetex"] else
                  r"$\lambda_{\rm mfp}$ (912 Å) [pMpc]")
    log_axis(a1, [0.5, 0.7, 1, 1.5, 2, 3])
    a1.set_ylim(0.4, 3.8)
    a1.set_ylabel(r"$\tau_{\rm eff}(84\%)-\tau_{\rm eff}(16\%)$, $\langle F\rangle$ = observed")
    for ax, tag in [(a0, "(a)"), (a1, "(b)")]:
        ax.set_xlim(ZMIN, ZMAX)
        ax.set_xlabel(r"$z$")
        ax.grid(alpha=0.3, lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_title(tag, loc="left", fontsize=9)
    # the observations and the fit marker in (a), upper right (empty there);
    # the runs in (b), upper left
    h0, l0 = a0.get_legend_handles_labels()
    keep = [i for i, l in enumerate(l0) if l in ("Becker et al. 2021", "Zhu et al. 2023", "exponential fit")]
    a0.legend([h0[i] for i in keep], [l0[i] for i in keep], fontsize=6.5, frameon=False, loc="upper right")
    a1.legend(fontsize=6.5, frameon=False, loc="upper left", handlelength=2.6)
    fig.tight_layout()
    out = os.path.join(HERE, "..", "figures", "fig_mfp_width")
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


if __name__ == "__main__":
    main()
