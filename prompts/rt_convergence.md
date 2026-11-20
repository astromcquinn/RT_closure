# Thread prompt (klone): convergence of the Γ fluctuations of M1 and of the rays

*Written 2026-11-20 for the "Shared limitations" item of main.tex (M1 the
least converged moment method; the rays' convergence untested). Paste
everything below the line into a Claude Code session on klone, in a checkout
of `astromcquinn/NewRadHydroCode`.*

---

Read CLAUDE.md, docs/STATUS.md (the 2026-11-20 entry) and docs/rt_moments.md
§7–8, then `tools/hyak/rt_convergence.sh` (its header describes both series)
and `tools/hyak/rt_suite512.sh` for the conventions. You are on UW Hyak klone
(`source tools/hyak/env.sh`, `RUNS=/gscratch/astro/$USER/radhydro/runs`).
Work on a branch off `claude/dreamy-ride-nchi0z` (it holds the script, the
uniform-opacity test `tools/analysis/moment_transfer.{cpp,py}` and §7–8);
commit often and push; one PR at the end. The branch changes no source of
`radhydro`, so a `build/radhydro` from current `main` is fine: check that it
exists and say which commit it was built from; rebuild with
`sbatch tools/hyak/build_hyak.sh` only if it is missing or older than the
suite's (6658086).

**Background.** In a uniform-opacity test of the code's transport (§7), M1's
Γ power above k ≈ (2/λΔx)^½ is set by the first-order GLF flux and by
`moment_inject = 1`, not by the closure: with λ equal to the box M1 crosses
above the exact transfer function at kΔx ≈ 1.3 at 32³, 64³ and 128³, and at
fixed kλ its amplitude falls toward the linear solution with resolution,
while OTVET is converged. The rays have not been tested: the suite ran with
`nray_max_factor = 15`, and rays outside the brightest quarter of the pool
merge into 48 cones per cell, well below the 64 rays per cell that Wu,
McQuinn & Eisenstein 2021 §5.2.3 assume (ℓ ≈ 8, converged for k ≲ ℓ/λ).
These runs test both in full reionization simulations.

1. **Dry run first.** `DRYRUN=1 tools/hyak/rt_convergence.sh all` and check
   the printed jobs: 3 ICs jobs (128³, 256³, 512³ gas with 512³ particles,
   20 Mpc/h; it reuses `$RUNS/rt512cal256/ics` for 256³ if present), 13
   whole-node runs (`rtconv_N{128,256,512}_rays`, `..._rays_m1` and
   `..._rays_m1_inj0`, M1 with `moment_inject = 0`;
   `rtconv_N256_rays_f{8,32,64,120}`), 4 analysis jobs. The script has only
   been dry-run and smoke-tested at toy size, never through Slurm: fix what
   breaks, and say what you changed. Check the free space under `$RUNS`
   against the suite's disk estimates (rt_suite512.sh header) before
   submitting. **Ask me before submitting the three 512³ runs** (4-day limit,
   a node each); submit the rest with `RES="128 256"`.
2. **Before the runs start, verify the matched sources.** After the ICs
   jobs: `xv_dm.init` must be byte-identical in the three ICs directories
   (md5sum). After the first snapshot with sources of the 128³ and 256³ ray
   runs: compare the halo catalogues or the source count and total
   luminosity in `run.log` / `ray.log`; they should agree to a few per cent
   (the gas's gravity differs). If they do not, stop and report.
3. **Babysit.** A run that hits its time limit continues from its checkpoint
   when resubmitted (`reion_production.slurm`); the analysis jobs fire on
   `afterany` and will miss its late snapshots, so rerun
   `tools/hyak/rt_convergence.sh post` once every run has `run/DONE`. For
   the ray-budget runs record the peak RSS and, from `ray.log`, the live
   rays per cell after overlap and how often the pool guard limited splits
   or forced merges: that is the actual angular resolution of each run.
4. **Resolution series (M1).** From `$RUNS/rtconv_post/N{128,256,512}/gamma_pk.txt`
   (field `gammaHI_avg`): P_Γ(M1)/P_Γ(rays) and r(k) at fixed k, at matched
   x_V ≈ 0.5, 0.8, 0.96 and after overlap (z ≈ 5), against N. The histories
   will differ with resolution: give z(x_V) and the mean free path of every
   run at the compared snapshots (the suite's λ_mfp estimator,
   `tools/hyak/igm_diag.slurm`), and compare at matched x_V, not matched z.
   Predictions of §7 to confirm or refute: after overlap the ratio falls
   with N at k ≳ 1 h/Mpc; M1 overtakes the rays at kΔx ≈ 1.3 at every N
   (so at k ∝ N); at k ≲ 0.5 h/Mpc the ratio does not depend on N. Also
   report whether the rays themselves change with N at fixed k (they are the
   reference, and the absorbers change with the gas resolution).
   **The injection order.** `M1_inject0` in the same tables is M1 with the
   sources injected before the transport. In the uniform-opacity test
   T(inject 1) − T(inject 0) = 1 − exp(−Δx/λ) at every k and resolution (a
   white term: the current substep's photons in their source cells), and
   inject 0 is nearer the continuum M1 solution but smooths the sources
   over ~2 cells. Report P_Γ(M1 inject 0)/P_Γ(rays) beside M1's: how much
   of M1's excess over the rays at kΔx ≳ 0.5 is this term, whether inject 0
   stays below the rays at every k, and whether its ratio depends less on
   N. Also report inject 0's known cost in these runs: the neutral fraction
   and Γ in cells above 100 ρ̄ after overlap against the rays and inject 1
   (docs/rt_moments.md §5a).
5. **Ray-budget series.** From `$RUNS/rtconv_post/rays/gamma_pk.txt`
   (reference f120): P_Γ(f)/P_Γ(f120) and r(k) for f = 8, 15, 32, 64 at the
   same epochs, and the same for x_HII (`tools/analysis/reion_power.py` or
   `rt_suite_figures.py`). Is f = 15, the suite's value, within 10 % of
   f120 at k ≤ 2 h/Mpc after overlap, and up to which k? Does the
   difference grow with λ (later snapshots), as k ≲ ℓ/λ would predict? Also
   compare the global quantities: x_V(z), the median Γ_HI of the ionised
   gas, λ_mfp. If f64 and f120 still differ, say so: then the rays are not
   converged at any budget we can run, and `nside_merge` (fixed at 2 in the
   code, no params.txt key) is the next thing to vary; do not add that key
   without asking.
6. **Write up.** One figure per series (P_Γ ratio and r(k) against k, one
   line per N or per f, panels by epoch) with their txt files in
   `docs/figures/`, a results subsection in docs/rt_moments.md §8, and
   docs/STATUS.md. State plainly what was and was not run. Then propose the
   wording for main.tex's "Shared limitations" item (do not edit the paper
   repository; give me the sentences): the measured change of M1's P_Γ ratio
   per doubling of N, and the k up to which the suite's rays are converged
   in the ray budget.

Ground rules that matter here: the defaults must stay bit-identical to the
Fortran (CLAUDE.md), so no source changes on this thread beyond the tools;
never restart or modify the suite's own runs (`reion512*`); the Fortran
submodule is private.
