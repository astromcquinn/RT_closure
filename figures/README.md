# Figures

Drafts are copies of the report figures of the code repository,
`astromcquinn/NewRadHydroCode`, `docs/figures/` at `main` (2bc8f62). The
final figures are made on klone (outline.md §3, §6). Record the code commit
and the command of each final figure here.

| file | paper | source (NewRadHydroCode) | made by | status |
|---|---|---|---|---|
| `fig1_maps_xHII_draft.png` | Fig. 1 | `docs/figures/taueff_21cmfast_fig8_maps.png` (branch `21cmfast-mass-sources`, 61b8312): rows z = 6.97, 6.20, 5.70; columns rays, M1, OTVET, cone, 21cmFAST (mass-dependent sources matched to the suite, R_max = 15 Mpc, on the suite's density) | `scripts/fig1_compose_draft.py` (this repository) | draft; final from the cubes |
| `fig_gamma_maps_draft.png` | Γ maps | `docs/figures/rt_suite_512_maps_gamma.png` (e800544), the x_V = 0.49 row cut and the colour bar redrawn (LogNorm 1e-14–1e-11, magma) | crop by hand (2026-11-06); final: `rt_suite_figures.py --xv-gamma 0.8,0.97,1.0` | draft |
| — | profiles | — | `tools/analysis/gamma_profile.py` (NewRadHydroCode, branch `claude/beautiful-archimedes-kcgsvx`) on the 512³ suite | to make on klone |
| `fig2_pk_xHII_draft.png` | Fig. 2 | `docs/figures/rt_suite_512_pk_xHII.png` (e800544) | `rt_suite_figures.py` | draft: content final, paper style to do |
| `fig3_pk_gamma_draft.png` | Fig. 3 | `docs/figures/rt_suite_512_pk_gamma.png` (e800544) | `rt_suite_figures.py` | draft: epochs by x_V; final at z ≈ 6.0, 5.5, 5.0 (a `--z` option) |
| `fig4_schematic.{pdf,png}` | Fig. 4 | — | `scripts/fig4_schematic.py` (this repository) | first version |
| `fig5_tensor_draft.png` | Fig. 5 | `docs/figures/otvet_closure_apriori.png` (dca5c9a) | `tools/analysis/tensor_compare.py`, `tensor_summary.py` on the 256³ dumps | draft: six panels, prototype tensors; final two panels with `apps/otvet_tensor` at all 13 redshifts |
| — | Fig. 6 | — | from `docs/otvet_closure.md` §3 tables | to make: the normalisation |
| `fig_mfp_width.{pdf,png}` | λ_mfp and τ_eff width | `data/taueff_mfp_snap_A.txt` (from `docs/figures/taueff_21cmfast_z_snap_A.txt`, branch `taueff-21cmfast`, 88e686d) and `data/lambda_mfp_obs.txt` (`data/igm/igm_z5_6.txt`) | `scripts/fig_mfp_width.py` (this repository) | final for the current runs |
| `fig8_21cmfast_pk_draft.png` | 21cmFAST comparison | `docs/figures/taueff_21cmfast_fig8_pk.png` (branch `21cmfast-mass-sources`, 61b8312) | `excursion_set.py figure` | draft: colours to unify with Figs. 2–3 |
