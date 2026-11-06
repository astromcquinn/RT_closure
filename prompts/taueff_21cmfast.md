# Thread prompt (klone): τ_eff over 50 Mpc/h segments, and 21cmFAST against the RT methods

*Written 2026-11-06 for outline.md (figures 7 and 8). One thread does both
parts, in the order below. Paste everything below the line into a Claude
Code session on klone, in a checkout of `astromcquinn/NewRadHydroCode`.*

---

Read CLAUDE.md, docs/STATUS.md, docs/rt_suite_512.md (§1, §4, §6, §7),
docs/igm_diagnostics.md and the header of data/igm/igm_z5_6.txt, then
tools/analysis/igm_stats.py, igm_plot.py, rt_suite_figures.py and
gamma_power.py. You are on UW Hyak klone (`source tools/hyak/env.sh`,
`RUNS=/gscratch/astro/$USER/radhydro/runs`). Branch `taueff-21cmfast` off
`main`; commit often and push; one PR at the end. Other threads may be
working on `absorbers-wu21` and on the Γ profiles: keep your edits to
shared tools additive (new options, defaults unchanged).

**The runs** (read only; never write into them): the uniform 512³ suite,
40 Mpc/h, `$RUNS/reion512_rays` (case B, the reference), `_caseA` (case A +
recombination radiation), `_m1`, `_otvet` (thin), `_otvet_split`,
`_otvet_screen`, `_otvet_cone`. The final set used f6 = 0.11 and the
continuous ĉ schedule (`c_reduced_schedule_interp = 1`); the table in
docs/rt_suite_512.md §1 is stale, so take every parameter, the cosmology
included, from each run's `params.txt`. The 3D snapshots, with x_HI, T,
ρ_gas, `gammaHI`, `gammaHI_avg` and `Gas/u_gas`, are at about z = 6.97,
6.5, 6.20, 5.98, 5.70, 5.49, 5.25 and 4.99. Compare at fixed z (user
decision). Write the outputs under `$RUNS/rt_closure_paper/`.

## Part A: the τ_eff distribution over 50 Mpc/h segments

1. **Per-segment τ_eff at the snapshots.** Extend `igm_stats.py` (a new
   option; the default output unchanged) to keep the flux of each
   redshift-space skewer it already builds (Hubble flow plus peculiar
   velocity, thermal broadening). From it, form τ_eff = −ln⟨F⟩ per segment:
   - box-length segments (40 Mpc/h), and
   - 50 Mpc/h segments, each a box-length skewer joined to 10 Mpc/h of
     another, randomly chosen skewer at the same z. Say so in the report:
     the joined segment is not one physical sightline, and the box misses
     the fluctuations on scales above 40 Mpc/h, so the scatter is a lower
     bound.

   Do this for every run at z ≈ 6.20, 5.98, 5.70, 5.49, 5.25 and 4.99, both
   raw and with τ rescaled by the factor A that matches the Bosman et al.
   2022 mean flux at that z (`igm_stats.py` already computes A). The
   rescaled distributions isolate the scatter, which follows the Γ
   fluctuations: expect thin OTVET broader than the rays and M1 narrower.
2. **Figure 7:** the cumulative τ_eff distribution (rescaled) per method at
   three redshifts (about 5.98, 5.49, 4.99), and the 16/50/84 % points of
   τ_eff against z for every method. Fixed colours and line styles as in
   `rt_suite_figures.py`. Text table of every number.
3. **Observed distributions:** the repository has Bosman+22's mean
   transmission only (`data/igm/igm_z5_6.txt`), not their τ_eff
   distributions. Do not transcribe them from memory: ask the user for the
   paper's table, and until then compare the methods with each other and
   with the observed mean.
4. **Optional, finer in z:** the movie slabs (`movie/frame_NNNNN_<field>.slab`,
   `movie/slab.txt`; 8 cells thick through the box centre, every Δz =
   0.025, with x_HI, T and ρ but no velocities) allow real-space skewers
   along the slab plane. If cheap, compute the real-space τ_eff scatter
   against z from them, and calibrate it against the redshift-space values
   at the snapshot redshifts, where both exist. Report the real-space
   offset before using it.

## Part B: 21cmFAST against the rays and the moment methods

1. **Install and check** 21cmFAST (`py21cmfast`) in a conda environment on
   klone (it needs GSL and FFTW; use the modules or conda packages). Record
   the version. From its documentation, find whether it can run on an
   external density field or initial conditions. Do not rely on remembered
   API details.
2. **B1, the same density field (the comparison for the paper).** At each
   snapshot during reionization (z ≈ 6.97, 6.5, 6.20, 5.98, 5.70), apply
   the 21cmFAST excursion-set criterion to the suite's own gas density.
   A cell is ionised when ζ f_coll(R) ≥ 1 on any smoothing scale R, from
   R_max down to the cell, with f_coll from the conditional collapse
   fraction of the smoothed density. Use 21cmFAST itself if it accepts the
   field; otherwise implement the criterion directly (FFT top-hat
   smoothing; the formula from 21cmFAST's documentation or source, cited
   by file and version).
   - Choose ζ at each z so that the volume-weighted x_HII equals the rays'
     at that z. Report ζ(z), and R_max (try the 21cmFAST default and a
     value set by the runs' mean free path).
   - Compare with every run, as in Figure 2: Δ² of x_HII, the ratio to the
     rays, r(k) with the rays, and the fraction of cells whose x_HII differs
     from the rays' by more than 0.5. Add 21cmFAST as one more curve to the
     x_HII power figure, and one more column to the x_HII maps (same slab).
   - Optional variant: the criterion on the sources' emissivity instead of
     f_coll(δ), if a source field is available (see
     prompts/gamma_profiles.md, step 3, for `Luv.bin`; the gas-density
     peaks otherwise).
3. **B2, a standalone 21cmFAST run (statistics only).** The suite's
   cosmology, box (40 Mpc/h) and resolution (512³, or 256³ if memory
   requires), its own initial conditions, its parameters tuned to the rays'
   x_V(z). Compare Δ² of x_HII at matched x_V with the suite's spectra
   (`docs/figures/rt_suite_512_pk.txt`). Say in the report that two
   realisations of a 40 Mpc/h box differ substantially at low k.
4. **Figure 8:** B1 in the style of Figure 2, plus the maps column.

## Reporting

- Tools: the `igm_stats.py` option (with a test on a synthetic cube under
  the existing analysis tests, if any), `tools/analysis/taueff_plot.py`,
  `tools/analysis/excursion_set.py` (B1, with a test: a single spherical
  overdensity is ionised out to the radius the criterion gives).
- A report `docs/taueff_21cmfast.md` with the figures, the tables, ζ(z),
  the 21cmFAST version and settings; docs/STATUS.md and docs/PLAN.md.
- Network rule: arXiv, ADS and journal sites are not reachable from klone.
  Package indexes and GitHub may be; check. Flag every reference from
  memory (21cmFAST: Mesinger, Furlanetto & Cen 2011; the version-3 code
  paper by Murray et al. 2020; τ_eff over 50 Mpc/h: Becker et al. 2015 and
  Bosman et al. 2018/2022) for the user to verify.
- Ask the user before any run that needs more than one node-day.
