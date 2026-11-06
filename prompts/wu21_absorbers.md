# Thread prompt (klone): why the closures don't change the mean Γ_HI after overlap

*Written 2026-11-06 for the paper in this repository (outline.md, §5 of the
outline: "IGM statistics the same for every method"). Paste everything
below the line into a Claude Code session on klone, in a checkout of
`astromcquinn/NewRadHydroCode`.*

---

Read CLAUDE.md, docs/STATUS.md, docs/rt_suite_512.md (§1, §4, §5, §7),
docs/otvet_closure_literature.md §1 ("Absorbers and mean free path"),
docs/port_notes.md §5b (P11) and docs/igm_diagnostics.md, then
tools/analysis/igm_stats.py and gamma_power.py (file formats, units,
cosmology). You are on UW Hyak klone (`source tools/hyak/env.sh`,
`RUNS=/gscratch/astro/$USER/radhydro/runs`). Branch `absorbers-wu21` off
`main`; commit often and push; one PR at the end.

**The question.** Wu, McQuinn & Eisenstein 2021 (JCAP 02, 042,
arXiv:2009.07278, §4; summarised in docs/otvet_closure_literature.md §1,
read through a summarising tool, so check the numbers against the paper if
you quote them) find that moment closures over-ionise self-shielding
absorbers: the recombination rate in an r⁻² absorber is about 1.3× the
exact one for OTVET and 1.4× for M1, so at fixed emissivity the moment
methods' Γ_HI is about 0.4× the exact one and the effective mean free path
is biased. In our uniform 512³ suite (40 Mpc/h, `$RUNS/reion512_rays*`)
nothing like this shows: the median Γ of the ionised cells agrees between
the rays and every moment method to ≤ 10 % from z = 12 to 5
(docs/rt_suite_512.md §5), and so do Γ, λ_mfp and ⟨F⟩ at z = 5–6 (§7). Find
out why. Three hypotheses, not exclusive:

- **H1, resolution.** The cells are 78 kpc/h comoving; λ_mfp is 3.5–5× the
  observed in every run, the rays included, so Lyman-limit systems are
  probably under-resolved and absorbers hold too small a share of the
  photon sink for the closure to matter.
- **H2, the dense-gas rule.** The suite ran from 2026-10-21 to 10-22, before
  P11 became part of `legacy_physics = 0` (2026-10-28, commit aa30151).
  It therefore used the original rule: in a cell denser than 50× the mean,
  `photo_cell` removes only x = min(exp(−(δ − 50)/50), 1) of the photons its
  photoionisations use (0.37 at δ = 100, 0.02 at δ = 250), so the densest
  gas neither consumes nor shields. Confirm this from the runs' `params.txt`
  and the binary (`$RUNS/rt_suite512_bin/radhydro_interp`; the commit id
  `df3f26a` recorded in docs/STATUS.md is from the pre-move repository, so
  find the build date or the source it was built from rather than that id).
- **H3, the sink is elsewhere.** If the photons are lost mostly to the
  diffuse IGM's recombinations, to redshifting out of the groups and to the
  light horizon at the reduced ĉ, the absorbers do not set ⟨Γ⟩ whatever the
  closure.

**Phase 1: existing data only (do this first; no new runs).** On the
snapshots at z ≈ 5.98, 5.49, 5.25 and 4.99 of `reion512_rays` (case B, the
reference), `_m1`, `_otvet`, `_otvet_cone` (and `_otvet_split`,
`_otvet_screen` if cheap), with Γ from `gammaHI_avg`:

1. **Where the photons go, by density.** Per cell, the hydrogen
   photoionisations Γ n_HI V and the case-B recombinations α_B(T) n_e n_HII V
   (take α_B and the electron density from the code's own rate functions,
   not from memory). With the original rule, the photons actually removed
   are x(δ) times the photoionisations. Bin by δ (log bins) and by x_HI. Give
   the fractions of the box's removed photons, and of its recombinations, in
   δ > 10, 50 and 100 and in cells with x_HI > 0.1 and > 0.5. Also give the
   photons that would be removed with x = 1 (P11 on), to size H2. Put these
   next to the photon budget of each run's `ray.log` at the same steps
   (`Moments :` lines: in flight, injected, absorbed, lost; the rays' budget
   line), so absorption in dense gas can be compared with absorption
   elsewhere and with the redshift losses (H3).
2. **Self-shielding curves.** The median Γ and x_HI against δ for each
   method. Take the self-shielding density from the data (the δ where the
   rays' median x_HI reaches 0.5), not from a formula.
3. **Wu's mechanism at our resolution.** In δ bins above 10, the ratio of
   each moment method's total recombination rate to the rays' at the same
   z. Wu+21 predict roughly 1.3–1.4× for resolved absorbers. Report what we
   get, and in how much of the photon sink it applies.
4. **How resolved the absorbers are (H1).** In the rays at z ≈ 5.5 and 5.0:
   connected regions of x_HI > 0.5 (periodic), their sizes in cells and
   their HI columns along the axes (N_HI ≈ Σ n_HI Δx). How many reach
   Lyman-limit columns (N_HI > 1.6×10¹⁷ cm⁻²), and what fraction of the
   volume-averaged 912 Å opacity σ n_HI comes from cells with a per-cell
   τ_912 > 1?

Write the tool as `tools/analysis/absorber_budget.py` (with a small test on
a synthetic cube, run by ctest under the `analysis` label if one exists),
the report as `docs/absorbers_closures.md` (tables, one figure of the sink
fractions and the Γ(δ) curves per method), and the lines of docs/STATUS.md
and docs/PLAN.md. **Report which of H1–H3 the numbers support, with the
fractions.**

**Phase 2: propose, don't run.** From what Phase 1 finds, propose a
controlled test with node-hours and disk, for the user's decision. Options
to cost:
- (a) H2 at fixed resolution: 256³ in 20 Mpc/h (the cell of the suite) with
  the rays, M1 and the cone, each with `photon_consume_dense = 1` and `= 0`.
- (b) H1: the same three methods at 512³ in 20 Mpc/h (39 kpc/h cells), P11
  on. Mind the sources: a finer mass resolution lowers the FoF floor and
  changes the luminosity density (the suite's first launch ionised the box
  by z ≈ 9 for that reason, docs/rt_suite_512.md §1b), so keep the source
  luminosity density fixed or recalibrate f6 in a precheck.
- (c) Wu+21's own §4 problem, one self-shielding absorber in a uniform
  background, with each closure, if the code can set it up (check the
  plane-parallel mode, docs/plane_parallel.md, and the rt_driver problems).

Do not launch Phase 2 runs without the user's go-ahead. arXiv, ADS and
journal sites are not reachable from klone: take nothing about Wu+21 beyond
the literature notes, and ask the user for the paper if needed.
