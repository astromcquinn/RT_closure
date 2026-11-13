# Figures

Drafts are copies of the report figures of the code repository,
`astromcquinn/NewRadHydroCode`, `docs/figures/` at `main` (2bc8f62). The
final figures are made on klone (outline.md §3, §6). Record the code commit
and the command of each final figure here.

**Late-end suite (2026-11-12).** Figs. 1–4 and `fig_mfp_width` are now made from
the late-end 512³ suite on klone, `/gscratch/astro/mcquinn/radhydro/runs/reion512late*`
(rays, case A + RR, M1, OTVET with the Gnedin & Abel 2001 background
`otvet_background = ga01`, screen, cone; f6 = 0.10, P11, no SN heating; binary
and analysis tools NewRadHydroCode main 6658086). The split was not rerun. The
older `*_draft` files and rows below are from the earlier suite (f6 = 0.11).
`R = /gscratch/astro/mcquinn/radhydro/runs`; the data job is
`$R/reion512late_figures/paper/paper_data.sh`, the map job `maps.sh` beside it.

| file | paper | source (NewRadHydroCode) | made by | status |
|---|---|---|---|---|
| `fig1_maps_xHII_draft.png` | Fig. 1 | `docs/figures/taueff_21cmfast_fig8_maps.png` (branch `21cmfast-mass-sources`, 61b8312): rows z = 6.97, 6.20, 5.70; columns rays, M1, OTVET, cone, 21cmFAST (mass-dependent sources matched to the suite, R_max = 15 Mpc, on the suite's density) | `scripts/fig1_compose_draft.py` (this repository) | superseded by `fig1_maps_xHII.png` |
| `fig_gamma_maps_draft.png` | Γ maps | `docs/figures/rt_suite_512_maps_gamma.png` (e800544), the x_V = 0.49 row cut and the colour bar redrawn (LogNorm 1e-14–1e-11, magma) | crop by hand (2026-11-06); final: `rt_suite_figures.py --xv-gamma 0.8,0.97,1.0` | draft |
| — | profiles | — | `tools/analysis/gamma_profile.py` (NewRadHydroCode, branch `claude/beautiful-archimedes-kcgsvx`) on the 512³ suite | to make on klone |
| `fig2_pk_xHII_draft.png` | Fig. 2 | `docs/figures/rt_suite_512_pk_xHII.png` (e800544) | `rt_suite_figures.py` | draft: content final, paper style to do |
| `fig3_pk_gamma_draft.png` | Fig. 3 | `docs/figures/rt_suite_512_pk_gamma.png` (e800544) | `rt_suite_figures.py` | draft: epochs by x_V; final at z ≈ 6.0, 5.5, 5.0 (a `--z` option) |
| `fig4_schematic.{pdf,png}` | Fig. 4 | — | `scripts/fig4_schematic.py` (this repository) | first version |
| `fig5_tensor_draft.png` | Fig. 5 | `docs/figures/otvet_closure_apriori.png` (dca5c9a) | `tools/analysis/tensor_compare.py`, `tensor_summary.py` on the 256³ dumps | draft: six panels, prototype tensors; final two panels with `apps/otvet_tensor` at all 13 redshifts |
| — | Fig. 6 | — | from `docs/otvet_closure.md` §3 tables | to make: the normalisation |
| `fig_mfp_width.{pdf,png}` | λ_mfp and τ_eff width | `data/taueff_mfp_snap_A.txt` (late-end suite: `igm_stats.py --taueff 50 --lya-only --nskew 8192 --seed 1`, `taueff_plot.py`, `taueff_z.py --norm --full`; λ_mfp from `$R/reion512late_igm/igm_*.json`) and `data/lambda_mfp_obs.txt` (`data/igm/igm_z5_6.txt`) | `scripts/fig_mfp_width.py` (this repository) | final for the late-end suite |
| `fig8_21cmfast_pk_draft.png` | 21cmFAST comparison | `docs/figures/taueff_21cmfast_fig8_pk.png` (branch `21cmfast-mass-sources`, 61b8312) | `excursion_set.py figure` | draft: colours to unify with Figs. 2–3 |
| `fig1_maps_xHII.png` | Fig. 1 | cubes of `$R/reion512late{,_m1,_otvet_ga01,_otvet_cone}` and the 21cmFAST run-mass output `$R/rt_closure_paper/es_late/es_rmax15_mass` (E-INTEGRAL, R_max = 15 Mpc, α★ = a(z) − 1 = 0.447/0.433/0.433, α_esc = 0, normalised to the rays' x_V) | `scripts/fig_maps.py --field xHII --steps 69,84,93` (this repository; panels in `fig1_maps_xHII_panels.txt`) | final for the late-end suite |
| `fig2_pk_xHII.{pdf,png}` | Fig. 2 | `data/pk_xHII_21cmfast.txt` (`excursion_set.py figure $R/rt_closure_paper/es_late RUN:label … --es rmax15_mass --steps 69,84,93`) | `scripts/fig_pk.py` (this repository) | final for the late-end suite |
| `fig3_gamma_maps.png` | Fig. 3 | `gammaHI_avg` cubes of the six late-end runs | `scripts/fig_maps.py --field gamma --steps 84,93,99` (this repository; panels in `fig3_gamma_maps_panels.txt`) | final for the late-end suite |
| `fig4_pk_gamma.{pdf,png}` | Fig. 4 | `data/pk_suite.txt` (`rt_suite_figures.py RUN:label … --xv 0.5,0.8,0.97 --xv-gamma 0.5,0.8,0.97,1.0`) | `scripts/fig_pk.py` (this repository) | epochs by x_V (0.54, 0.80, 0.96, 1.00); alternative at z ≈ 6.0, 5.5, 5.0 |
