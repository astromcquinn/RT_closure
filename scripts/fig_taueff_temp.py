#!/usr/bin/env python3
"""What sets the tau_eff scatter: the 50 Mpc/h tau_eff distribution of one run
(default the rays) with Gamma_HI and/or the temperature of the ionized gas
(x_HI < 1e-2) made uniform, tau rescaled to Bosman et al. 2022's mean flux in
every variant.

  left:   the 84-16 % width against z for the five variants
  others: the tau_eff PDF at the lowest and highest snapshot redshift

  own   the run's x_HI and T
  uG    x_HI * Gamma/Gamma_ref                 (uniform Gamma)
  uT    x_HI * (T/T_ref)^0.7 and T -> T_ref    (uniform temperature)
  uGT   both (density, velocities and the remaining neutral gas only)
  ion   uGT, and the cells with x_HI >= 1e-2 also at T_ref and in
        photoionization equilibrium with Gamma_ref (density and velocities
        only)

Data: data/taueff_temp.txt, data/taueff_temp_pdf.txt (made on klone by
$R/reion512late_figures/paper/taueff_temp.py).

usage: python3 scripts/fig_taueff_temp.py [--run rays]
       (writes figures/fig_taueff_temp.{pdf,png}; _<run> for another run)
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
KINDS = [("own", r"own $\Gamma_{\rm HI}$ and $T$", "#000000", "-", 2.0, 6),
         ("uG", r"uniform $\Gamma_{\rm HI}$", "#2a78d6", "--", 1.5, 9),
         ("uT", r"uniform $T$", "#eb6834", "-.", 1.5, 12),
         ("uGT", r"uniform $\Gamma_{\rm HI}$ and $T$", "#6b6a66", ":", 1.8, 15),
         ("ion", r"same, and no neutral gas", "#1baf7a", "-", 1.1, 18)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="rays")
    a = ap.parse_args()
    tab = np.array(sorted([float(v) for v in l.split()[1:]] for l in open(os.path.join(DATA, "taueff_temp.txt"))
                          if l.split() and l.split()[0] == a.run))
    pdf, cur = {}, None
    for line in open(os.path.join(DATA, "taueff_temp_pdf.txt")):
        t = line.split()
        if line.startswith("#P"):
            cur = pdf.setdefault((float(t[2]), t[3]), []) if t[1] == a.run else None
        elif t and not line.startswith("#") and cur is not None:
            cur.append((float(t[0]), float(t[1])))
    zs = sorted({z for z, _ in pdf})
    plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.8, "axes.edgecolor": "#52514e"})
    fig, (a0, a1, a2) = plt.subplots(1, 3, figsize=(7.2, 2.6))
    for kind, label, c, ls, lw, col in KINDS:
        a0.plot(tab[:, 0], tab[:, col], color=c, ls=ls, lw=lw, marker="o", ms=3, label=label)
        for ax, z in ((a1, zs[0]), (a2, zs[-1])):
            d = np.array(pdf[(z, kind)])
            ax.plot(d[:, 0], d[:, 1], color=c, ls=ls, lw=lw)
    a0.set_yscale("log")
    a0.set_yticks([0.5, 0.7, 1, 1.5, 2, 3])
    a0.set_yticklabels(["0.5", "0.7", "1", "1.5", "2", "3"])
    a0.minorticks_off()
    a0.invert_xaxis()
    a0.set_xlabel(r"$z$")
    a0.set_ylabel(r"$\tau_{\rm eff}(84\%)-\tau_{\rm eff}(16\%)$")
    a0.legend(fontsize=6.5, frameon=False, loc="upper right", handlelength=3)
    for ax, z in ((a1, zs[0]), (a2, zs[-1])):
        r = tab[np.argmin(abs(tab[:, 0] - z))]
        ax.set_xlim(max(0, r[5] - 1.6 * r[6]), r[5] + 2.4 * r[6])
        ax.set_ylim(0, None)
        ax.set_xlabel(r"$\tau_{\rm eff}$")
        ax.set_ylabel(r"$dP/d\tau_{\rm eff}$")
        ax.text(0.96, 0.94, f"$z={z:.2f}$", transform=ax.transAxes, ha="right", va="top")
    for ax in (a0, a1, a2):
        ax.grid(alpha=0.3, lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = os.path.join(HERE, "..", "figures", "fig_taueff_temp" + ("" if a.run == "rays" else "_" + a.run))
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=300)
    print("wrote", os.path.normpath(out) + ".{pdf,png}")


if __name__ == "__main__":
    main()
