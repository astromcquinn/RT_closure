# Thread prompt (klone): Γ maps and stacked proximity-zone profiles

*Written 2026-11-06 for figures 1b and 1c of outline.md. Paste everything
below the line into a Claude Code session on klone, in a checkout of
`astromcquinn/NewRadHydroCode`.*

---

Read CLAUDE.md, docs/STATUS.md and docs/rt_suite_512.md (§1, §5–6), then
`tools/analysis/gamma_profile.py` and `tools/analysis/rt_suite_figures.py`.
You are on UW Hyak klone (`source tools/hyak/env.sh`,
`RUNS=/gscratch/astro/$USER/radhydro/runs`). Work on a branch off
`claude/beautiful-archimedes-kcgsvx` (it holds `gamma_profile.py` and its
test); commit often and push; one PR at the end.

1. **Test the tool:** `python3 tools/analysis/test_gamma_profile.py` on a
   compute node.
2. **Γ maps without the earliest epoch:** `rt_suite_figures.py` on the seven
   suite runs (`$RUNS/reion512_rays{,_m1,_otvet,_otvet_split,_otvet_screen,
   _otvet_cone,_caseA}/run`, the rays first) with `--xv 0.8,0.97
   --xv-gamma 0.8,0.97,1.0`, written as PDF as well as PNG. Then a second
   version zoomed on the brightest source cluster: add an option to crop
   the slab to a region (e.g. `--zoom x0,y0,size` in Mpc/h), plotting
   Γ/⟨Γ⟩_V on a range that shows the proximity zones after overlap.
3. **Sources for the stacked profiles.** The suite snapshots have no
   `Luv.bin` and no dark matter. First find whether a restart can supply
   it: each run kept one checkpoint (`restart_keep = 1`); report its step
   and redshift. If it is at or before the z ≈ 5.0 snapshot, restart a copy
   of the rays run (never in place) from it with `Luv` added to `fields`, to
   z = 5.0 only, and check that the restarted `gammaHI_avg.bin` is
   byte-identical to the original snapshot's before using its `Luv.bin`.
   Otherwise, and for the earlier redshifts, use `--sources rho`: gas-density
   peaks, which do not depend on the RT. Check them against `Luv.bin` where
   both exist (what fraction of the sources each finds, and whether the
   profiles agree), and against `--sources gamma` as a cross-check.
4. **Profiles:** `gamma_profile.py` on the same seven runs, `--z 6.0,5.5,5.0`
   (and 6.2 for the overlap era), `--field gammaHI_avg`, the source choice
   of step 3, `--ngroups 3`. Plot the brightest third; keep `all` and the
   others in the txt. Report the rays', M1's, thin OTVET's and the cone's
   profiles at r = 1–3 cells and 10 cells, as ratios to the rays.
5. Put the figures and their txt files in `docs/figures/` with a short
   section in docs/rt_suite_512.md (or a new docs/proximity_zones.md), and
   update docs/STATUS.md.

Expected, to confirm or refute: M1's excess near the sources much smaller
than the rays' (a local closure diffuses once the background dominates the
cell's photons); thin OTVET's excess larger than the rays' after overlap
(its thin tensor beams the background along the source directions); the
split and the cone close to the rays; the source cells of every moment
method brighter than the rays' (`moment_inject = 1`).
