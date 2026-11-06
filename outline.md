# Paper outline: moment-RT closures for reionization against ray tracing

*Outline and references for a short paper, 2026-11-05 (user request:
"not the paper, a minimal outline and references, more complete on the new
methods"). Sources: the uniform 512³ suite (`docs/rt_suite_512.md`), the
closure design and validation (`docs/otvet_closure.md`), the literature
notes (`docs/otvet_closure_literature.md`). Every `docs/`, `src/`,
`include/`, `tools/` and `data/` path below is in the code repository,
`astromcquinn/NewRadHydroCode`; this repository (private) holds the paper.
Figures are made on klone by threads (§6).*

Working titles:
- *An HI-attenuated Eddington tensor for moment radiative transfer of
  reionization, tested against adaptive ray tracing*
- *Moment closures for reionization against ray tracing: what the
  optically thin Eddington tensor gets wrong, and how to fix it*

## 0. The claim (three points)

1. **Two standard closures fail in opposite ways.** One code, with the same
   sources, ĉ, photon coupling and recombinations, gives:
   - **M1:** no proximity zones. Its fronts decorrelate from the rays'
     at a few Mpc, and after overlap P_Γ is ~25× too low at
     k ≲ 2 h/Mpc.
   - **Thin OTVET:** follows the rays to x_V ≈ 0.8, then has 11–14× the
     rays' P_Γ after overlap.
2. **The rays' own Eddington tensor, recorded in a 256³ run, shows why.**
   - During overlap, the thin tensor is too isotropic on large scales: it
     adds light from regions behind neutral gas.
   - After overlap, it is too anisotropic by λ_eff/0.61 L. This is the
     minimum-image normalisation error predicted by Wu, McQuinn &
     Eisenstein (2021), measured here directly.
3. **Three new closures.**
   - The **direct + diffuse split** costs nothing, but fixes only the
     after-overlap error.
   - The **screened periodic kernel** (Wu+21's remedy) uses one global λ,
     which hurts during overlap.
   - The **HI-attenuated cone tensor**, with a photon-budget cutoff and
     blended with the split, fixes both regimes for 7 % more wall time. It
     gives the rays' history to Δz = 0.02, the closest x_HII morphology at
     every stage, and P_Γ within 0.7–1.1× of the rays' at k ≤ 2 h/Mpc
     after overlap.

## 1. Data

**The uniform 512³ suite** (`docs/rt_suite_512.md` §1, `$RUNS/reion512_*`)
is the basis of Figures 1–3.

| run | method | role in the paper |
|---|---|---|
| `reion512_rays` | adaptive rays, case B | reference |
| `reion512_rays_caseA` | rays, case A + recombination radiation | shown in Figures 2–3 (user, 2026-11-05): the rays' own physics variation |
| `reion512_rays_m1` | M1 | historic |
| `reion512_rays_otvet` | OTVET, thin tensor | historic |
| `reion512_rays_otvet_split` | split | new |
| `reion512_rays_otvet_screen` | screen | new (baseline) |
| `reion512_rays_otvet_cone` | cone (defaults) | new |

Configuration:
- **Box and resolution:** 40 Mpc/h, 512³ gas cells (78 kpc/h), 1024³
  particles on the 2048³ PM mesh.
- **ICs:** Zel'dovich at z = 100, Eisenstein–Hu no-wiggle P(k).
- **Sources:** abundance matching to FoF halos with the Sheth–Tormen
  refit, log ξ_ion = 25.38, f_esc(z) = f6 ((1+z)/7)^2.5.
- **Reduced speed of light:** the continuous ĉ schedule in x_HII,V,
  0.1c → 0.5c.
- **Recombinations:** case B.
- **Hydro and flags:** unsplit hydro, `legacy_rt = legacy_physics = 0`.
- **Provenance:** binary `radhydro_interp` at commit `df3f26a`
  (`docs/STATUS.md`, "the uniform 512³ suite").
- **Stale config table:** the final set used **f6 = 0.11** and
  `c_reduced_schedule_interp = 1`. The table in `rt_suite_512.md` §1 still
  lists 0.135 and the step schedule. Take the values from the runs'
  `params.txt`.

What exists, and what it limits:
- **3D snapshots** at the nominal z = 15, 7, 6.5, 6.25, 6, 5.75, 5.5, 5.25
  and 5 (actual e.g. 6.97, 6.20, 5.98, 5.70, 5.49, 5.25, 4.99), with x_HI,
  T, ρ, `gammaHI` and `gammaHI_avg`. In the reference run, x_V = 0.49 at
  z = 6.97, 0.79 at 6.20 and 0.97 at 5.70.
- **Movie slabs** (8 cells thick) every Δz = 0.025.
- **One checkpoint per run**, the last. Power spectra are therefore
  possible only at the snapshot redshifts; an earlier epoch (e.g.
  x_V = 0.25, z ≈ 8) exists only as a slab image.

**The 256³ closure runs** (`docs/otvet_closure.md` §1, §5–6;
`$RUNS/otvcl256*`) are the basis of the tensor comparison (§3, Figure 5;
user, 2026-11-05: "use the 256³ for now at least").
- **Box and runs:** 20 Mpc/h with the same cell. Rays (`otvcl256`) carry
  `tensor_dump = 1`: the Γ-weighted angular moments S0, S1 and S2 of the
  rays' radiation per cell, at 13 redshifts from z = 10 to 5. Moment
  siblings: `_m1`, `_otvet`, `_otvet_{split,screen,screensplit,cone,cone2}`.
- **Configuration:** the first set's, not the suite's: constant ĉ = 0.2c,
  f_esc = 0.23, case A + recombination radiation.
- **To check on klone:** that the dumps still exist.

**Not used** (user, 2026-11-05): the 1024³ cone run
(`runs/reion1024_otvet_cone`). The cone in the paper is the suite's 512³
`reion512_rays_otvet_cone`.

**Comparisons are at fixed z** (user, 2026-11-05). Every run writes its
snapshots at the same redshifts. `rt_suite_figures.py` already pairs the
runs at the reference's snapshot redshift, and labels each epoch by the
rays' x_V there.

## 2. Outline

### 1. Introduction
- **Why the field matters:** moment RT is the workhorse of large
  reionization simulations (M1: RAMSES-RT, ATON, AREPO-RT/Thesan; OTVET:
  ART/CROC). The Γ_HI field after overlap feeds the Lyα forest, the mean
  free path and the τ_eff scatter.
- **Known issues:**
  - M1 merges beams and has no proximity zones.
  - The thin tensor has no shadows (Gnedin & Abel 2001; Petkova & Springel
    2009) and the box-size normalisation error (Wu+21).
  - Gnedin (2025) finds CROC and Thesan disagree on the Γ–source transfer
    function, with no ray-tracing reference.
- **What is new here:**
  1. one code, every closure and adaptive rays, with all other physics
     shared;
  2. the true Eddington tensor measured from the rays;
  3. three closures, including a cone-traced HI-attenuated tensor.

### 2. Simulations and radiative transfer
- **2.1 Code and simulation:** a C++ port of the Trac & Cen RadHydro with
  the configuration of §1. Keep this short and cite the suite document's
  numbers.
- **2.2 Adaptive ray tracing:** the reference. HEALPix rays split
  adaptively (Abel & Wandelt 2002), reduced ĉ, 5 frequency groups,
  photon-conserving deposit, `gammaHI_avg` (Γ averaged over the hydro
  step's substeps, which removes the rays' sampling noise).
- **2.3 The moment solver**, shared by every closure:
  - Equations for N_g and F_g per group, with
    ∂F/∂t + ĉ² ∇·(D N) = −absorption.
  - First-order GLF (Rusanov) flux with wave speed ĉ, 4 subcycles per RT
    substep (Courant number 1/4).
  - Absorption through the same cell physics as the rays (`photo_cell`),
    the same per-group redshifting, and photon conservation to float
    precision.
  - Sources injected isotropically into their cell (`moment_inject = 1`).
- **2.4 The two standard closures:**
  - **M1:** Levermore's χ(f).
  - **Thin OTVET:** h = S / tr S, with S = Σ_s L_s d dᵀ/|d|⁴ over minimum
    images, by FFT, once per hydro step.

### 3. The Eddington tensor of the rays (the diagnosis)
- **3.1 Measuring it:**
  - `tensor_dump` accumulates S0 = Σw, S1 = Σw n and S2 = Σw n nᵀ over
    the ray deposits, with w the Γ-weighted photons; h_true = S2/S0.
  - Sampling noise from odd against even substeps: 0.005–0.02 per cell.
- **3.2 Metrics** (`tools/analysis/tensor_compare.py`):
  - **Error:** the Frobenius distance |h − h_true| = √(Σ_ij (h_ij −
    h_true,ij)²) over all nine components, not normalised by |h_true|.
    It is averaged over the ionised cells (x_HII > 0.9), weighted by S0.
  - **Its scale:** both tensors have trace 1, so isotropic against one
    beam is √(2/3) ≈ 0.82, two perpendicular beams √2 (the maximum), and
    two beams at angle θ √2 sin θ. In the paper, divide the error by
    √(2/3) so that it shares A's scale.
  - **Anisotropy:** A = |h − I/3|/√(2/3). It is 0 for isotropic light, 1
    for one beam (or two opposite beams) and 0.5 for light spread evenly
    in a plane; it depends only on the eigenvalues.
  - **Blocks:** S0 h is summed over each 8³ block (0.625 Mpc/h at 256³ in
    20 Mpc/h) before normalising. A closure's h is weighted by the rays'
    S0, so every tensor describes the same radiation field. Directions
    that differ within a block cancel, so the block A measures coherent
    anisotropy on scales ≳ 0.6 Mpc/h: the part that sets the large-scale
    flux and P_Γ at k ≲ 3 h/Mpc, and nearly free of the rays' noise.
  - **Radiation-force error** (∇·(S0 h) against the true force, per k):
    for an appendix at most.
- **3.3 Before overlap:**
  - Thin OTVET is good in the bulk, with block error 0.06–0.09.
  - Its errors sit in the 10–20 % of ionised cells that are shadowed or
    have Γ < ⟨Γ⟩/2: error 0.27–0.40, and the truth is more beamed.
- **3.4 During overlap:**
  - Thin OTVET is *too isotropic* on large scales: block A is 0.32 against
    the truth's 0.42 at z = 7.4, and 0.41 against 0.72 at 24–48 cells
    from the nearest source.
  - Edge cells are lit from inside their own region; OTVET adds the
    regions behind the neutral gas.
- **3.5 After overlap, the normalisation:**
  - Per unit emissivity, ∫_cube d³r/(4πr²) = 0.610 L, so the anisotropy is
    right only while λ_eff ≈ 0.61 L.
  - Table: λ_eff/0.61 L, A_OTVET/A_true, median N/N_dir and P_Γ(OTVET)/rays
    at z = 6.2–4.9.
  - P_Γ excess ≈ (A_OTVET/A_true)² (heuristic). Wu+21's linear theory gives
    the k-independent ratio 4πλ/L_O (Appendix B).
- **3.6 What M1 does:** the oracle M1 (Levermore's D on the rays' true
  flux) is best in shadowed pre-overlap cells and worst on large scales in
  every regime. After overlap it is far too isotropic: A ≈ 0.02 against
  0.11.

### 4. New closures (the detailed part)

Notation (define once):
- N_g: photons of group g per mean H atom.
- q_g = fResc · ξ_g · Δt_RT/(V_cell ⟨n_H⟩): photons per unit L per
  substep, with ξ_g the group's share of ξ_ion.
- One RT substep is one cell of light travel.
- N_dir,g = q_g tr S/4π: the unattenuated steady-state photons of the
  current sources, minimum image.
- Γ-weighted sums: N_w = Σ_g σ_g N_g and q_w = Σ_g σ_g q_g.

**4.1 Direct + diffuse split** (`otvet_split = 1`)
- **Equation:** P_g = N_g I/3 + min(N_g, N_dir,g)(h − I/3), applied per
  group in every GLF subcycle.
  - If N ≤ N_dir: thin OTVET exactly.
  - If N > N_dir: the thin light's own pressure q_g S/4π, plus the excess
    photons as an isotropic gas.
  - Equivalently D = I/3 + β(h − I/3), with β = min(1, N_dir/N).
- **When N > N_dir:** N_dir counts only light that has travelled about
  L/2 or less (minimum image) from the current sources. The box budget
  gives ΣN/ΣN_dir ≈ λ_eff/0.61 L, the same factor as the anisotropy
  error. The solution measures it per cell and per group, with no λ.
- **Properties:**
  - Realizable: eigenvalues lie in [0, N], P is piecewise linear in N with
    slopes h and I/3, and the GLF update stays positive at speed ĉ.
  - Cost: one float per cell, no extra FFT.
- **Related work:** the CROC background split (Gnedin 2014, App. C) and
  the Gnedin & Abel (2001) background. Here the split is local and comes
  from the solution's own N.
- **Limits:**
  - It changes the amount of anisotropy, not its direction; it is
    identical to thin OTVET before overlap.
  - The diffuse part has no direction.
  - N_dir is unattenuated.

**4.2 Screened periodic kernel** (`otvet_closure = screen`; the baseline)
- **Kernel:** e^(−r/λ) d dᵀ/r⁴ over the 27 images, plus an isotropic
  continuum (4πλ e^(−R/λ)/L³) I/3 for the images beyond, where R ≈ 1.86 L
  is the radius of a sphere with the 27 boxes' volume.
- **λ from the budget:** λ = ΣN_w/(q_w ΣL), in cells. This is ĉ times the
  mean photon lifetime, so the screened light totals the photons held.
  It uses N at the start of the hydro step.
- **Why it fails during overlap:** one λ cuts every direction by distance
  alike. A priori, its 8³-block tensor is more isotropic than thin
  OTVET's at x_V = 0.74–0.94, and its force error at k = 0.47 h/Mpc is
  2.6–5.4× thin OTVET's at x_V = 0.61–0.86. In the 512³ suite its Γ is mottled during reionization, with
  2× the rays' P_Γ at k ≈ 2 h/Mpc.
- **Cost:** 6 FFTs per step, with no kernel caching because λ changes.

**4.3 The HI-attenuated cone tensor** (`otvet_closure = cone`)
- **Idea:** compute the direct light as the rays see it, attenuated by
  the HI along each direction, by voxel cone tracing through mip-maps.
  Cost is independent of the number of sources.
- **Algorithm**, once per hydro step:
  1. **Mip-maps** of the emissivity and of the HI column per cell. Each
     cell's group-1 τ is capped at 1 (`otvet_cone_taucap`), as a
     covering-fraction proxy: e^(−⟨τ⟩) ≠ ⟨e^(−τ)⟩.
  2. **Receivers** every 4 cells (`otvet_cone_coarse`), each with 192
     HEALPix cones (`otvet_cone_nside = 4`), half-opening ≈ 8°.
  3. **March** from r_c = 8 cells outward:
     - step = half the cone width, sampling the mip level whose cell size
       matches the width;
     - added light = emissivity × Ω × ds × T, with T = Σ_g W_g e^(−σ_g col)
       the Γ-weighted transmission of the source spectrum;
     - the light goes into n nᵀ per half-octave distance bin;
     - stop at T < 10⁻⁴ or at 8 boxes (`otvet_cone_smax`).
  4. **Near field** (r < r_c): the thin FFT, handed over smoothly to the
     cones between r_c and 2 r_c.
  5. **Budget cutoff:** a factor e^(−s/λ_x), with λ_x chosen by bisection
     over the stored bins (no second march) so that the direct light in
     ionised cells equals the photons held there.
     - No cutoff if the cones already hold fewer photons, or if the near
       field alone exceeds them.
     - Restricting the budget to ionised cells was needed: the
       unattenuated near field lit neutral gas around small H II
       regions.
  6. **Prolongation:** trilinear from receivers to cells, added to the
     near field, normalised.
  7. **Blend:** h = h_s + G_σ ∗ (h_cone − h_s), with σ = 4 cells and h_s
     the (Γ-weighted) split thin tensor. Eigenvalues are clamped to ≥ 0
     and the trace renormalised.
- **What it captures:**
  - Edge cells lit from their own region: block A 0.415 against the
    truth's 0.418 at z = 7.4.
  - Shadows of neutral islands and attenuation that varies with
    position.
  - After overlap, the normalisation, including the box scale, through
    the images and λ_x.
- **Related work:**
  - Finlator, Özel & Davé (2009): the same target with exact per-source
    long characteristics, at a cost ∝ cells × sources.
  - TreeCol and LEBRON-type columns; voxel cone tracing in graphics.
  - Davis, Stone & Jiang (2012): a short-characteristics VET.
- **Limits:**
  - Shadows narrower than a cone (≈ 0.29 s) are lost, as is per-source τ.
  - The τ cap is crude for self-shielded clumps.
  - One hydro step of lag in the HI and the budget.
  - Instantaneous sources, and a single gray tensor for all groups.

**4.4 Implementation**
- **Where it runs:** `moment_prep` once per hydro step; P_g in the
  transport each subcycle.
- **Reproducibility:** deterministic and independent of the thread
  count. The defaults are byte-identical to the original code. The
  AMReX backend gives the same results bit for bit
  (`docs/stage_e_moments.md`).
- **Speed:** FFT kernel spectra cached across steps; the six components
  transformed in parallel.
- **Cost:** a table of tensor time per step (256³: thin 0.7 s, screen
  1.2 s, cone 3.2 s) and the 512³ suite's wall times (thin 9 h 56 min,
  cone 10 h 35 min, rays 23 h 52 min).

**4.5 A priori validation** (Figure 5)
- Each closure applied to the rays' own sources and HI, against h_true,
  at the 13 dump redshifts: errors on cells (ionised, low-Γ, shadowed)
  and on blocks, the block anisotropy, and the force error and r(k) at
  k = 0.47–15 h/Mpc.
- Checks: the C++ tensors against the numpy prototypes
  (≤ 2.5·10⁻⁵ for the cones), and the unit tests.

### 5. Results at 512³
- **5.1 Histories:** one panel or a table. Every method agrees to 0.1 in
  z, τ_es to 0.0005, and the cone ends closest to the rays (Δz = 0.02).
  This is the photon budget at work: the closures redistribute the light,
  they don't change it.
- **5.2 Morphology** (Figure 1): M1's rounder fronts and missing
  proximity zones; thin OTVET's diffuse fronts and early-vanishing
  islands; the cone's sharp islands. The difference movie supports this.
- **5.3 x_HII power and r(k)** (Figure 2): the large scales agree for
  every method except M1. At k = 4.9 h/Mpc for x_V = 0.49 / 0.79 / 0.97,
  r(k) is:

  | method | x_V = 0.49 | 0.79 | 0.97 |
  |---|---|---|---|
  | cone | 0.92 | 0.86 | 0.65 |
  | thin OTVET | 0.85 | 0.69 | 0.30 |
  | M1 | 0.65 | 0.43 | 0.26 |

  The split equals thin OTVET here.
- **5.4 Γ_HI at z = 5–6** (Figure 3; `gammaHI_avg`):
  - P_Γ and r(k): thin OTVET is 11–14× the rays and M1 is 0.04–0.4×; the
    three new closures are within 0.7–1.9×, with r = 0.92–0.96.
  - The cone is closest at k ≤ 2 h/Mpc.
  - All moment methods are 1.6–1.9× at k ≈ 5 (sharper proximity zones
    without ray sampling).
  - Add the Γ PDF quantiles as a table.
  - Explain the agreement at kλ ≫ 1: once the anisotropy amplitude is
    right, P_Γ is the sources' 1/r² near field (Wu+21 eq. 5.15), so the
    closures converge. They differ on the box scale and during overlap.
- **5.5 IGM statistics:** one paragraph. Every method gives the same
  λ_mfp, ⟨F⟩ and median Γ against the data. The mean free path is
  3.5–5× too long in every run, for reasons unrelated to the closure
  (resolution and subgrid absorbers).

### 6. Discussion
- **Which closure to use:**
  - The cone for reionization runs.
  - The split as a free fix of existing OTVET codes after overlap.
  - Not the screen.
- **Shared limits of the moment methods:**
  - No shadows of self-shielded gas: the lower Γ tail is too narrow late.
  - Too little power at k ≳ 10 h/Mpc.
  - First-order GLF diffusion.
- **Relation to Gnedin (2025)'s CROC/Thesan comparison and to Wu+21's
  linear theory.**
- **Flux-limited diffusion, not run; expected failures** (reasoned, not
  measured). The flux is F = −ĉ λ(R) ∇N/κ, with R = |∇N|/(κN): it has no
  memory and always points down the local gradient.
  - No shadows: light flows around obstacles, so neutral islands are
    eaten from every side and self-shielded gas is over-ionised.
  - No crossing light: like M1, only the net flux down ∇N, with no beams
    through other light.
  - After overlap, in ionised gas R = λ_mfp |∇ln N| ≫ 1 almost everywhere
    in the box. The limiter then makes every photon a single beam down
    the gradient (|F| → ĉN, Eddington factor → 1), where the true light
    is nearly isotropic. That is the opposite extreme from M1, whose own
    fluxes cancel. Wu+21's linear theory, in which FLD at small R is plain
    diffusion like M1, holds only for fluctuations too weak to matter in
    the box. The sign of the resulting P_Γ error is not predictable
    without a run.
- **Extensions:** per-group cones, retarded sources, the cone on AMR
  levels.

### 7. Conclusions

### Appendices
- **A. Cone parameter study:** nside 2 → 4, receiver spacing 2 → 4, r_c
  4 → 8, the cutoff variants (λ_x ∈ {∞, λ_eff, 2λ_eff, budget}), blend σ;
  the `cmp_*` tables of `otvet_closure.md` §3.
- **B. The minimum-image normalisation:**
  - ∫_cube d³r/(4πr²) = 0.610 L, so L_O = 7.66 L.
  - The budget argument ΣN/ΣN_dir ≈ λ_eff/0.61 L.
  - The link to Wu+21's 4πλ/L_O.
- **C. (optional) Rays' sampling noise:** `gammaHI_avg` against the last
  substep; odd against even substeps.

## 3. Figures and tables

| # | content | data | tool | status |
|---|---|---|---|---|
| **1** | Reionization images: x_HII slabs (8 cells) with columns rays, M1, thin OTVET, cone and 21cmFAST (default parameters, R_max = 15 Mpc, on the suite's own density, ζ matched to the rays' x_V; user, 2026-11-06), rows z = 6.97, 6.20, 5.70 (x_V = 0.49 / 0.79 / 0.97) | suite snapshots; `excursion_set.py` output | draft: `scripts/fig1_compose_draft.py` from `taueff_21cmfast_fig8_maps.png`; final: `rt_suite_figures.py` with the 21cmFAST run as one more column (needs an option for runs without Γ) | draft; the 21cmFAST column to be replaced by the new source-matched run |
| **1b** | Γ_HI maps (`gammaHI_avg`, 8-cell slabs) at z = 6.20, 5.70, 4.99 (x_V = 0.79 / 0.97 / 1.00), all seven runs (user, 2026-11-06: the figure of the suite without its earliest row) | suite snapshots | `rt_suite_figures.py --xv-gamma 0.8,0.97,1.0` | draft in `figures/fig_gamma_maps_draft.png` (cropped from `rt_suite_512_maps_gamma.png`) |
| **1c** | Stacked Γ(r)/⟨Γ⟩_ion around the sources (brightest third) at z ≈ 6.0, 5.5, 5.0, with a 1/r² streaming guide and the ratio to the rays: the proximity zones (M1 none, thin OTVET the background beamed, cone like the rays) | suite snapshots; sources from `Luv.bin` if a restart writes it, else gas-density peaks | `tools/analysis/gamma_profile.py` (NewRadHydroCode, tested on synthetic cubes) | to make on klone (`prompts/gamma_profiles.md`) |
| **2** | Δ² of x_HII, the ratio to the rays and r(k) at z = 6.97, 6.20 and 5.70: M1, thin, split, screen, cone and the case A + RR rays | suite snapshots | `rt_suite_figures.py` `pk_xHII.png` (case A + RR already in it) | exists; paper style |
| **3** | Δ² of δ_Γ (`gammaHI_avg`), the ratio and r(k) at z = 6.0, 5.5 and 5.0: every method and the case A + RR rays | suite snapshots | `rt_suite_figures.py`; it chooses epochs by the rays' x_V, so it needs a `--z` option for the after-overlap redshifts | to make |
| 4 | Schematic of the closures: the split's budget picture and the cone march | — | drawn | to make |
| **5** | The tensor comparison, two panels against z (or x_V): (top) block-8³ anisotropy A of the rays (black, labelled "rays": their tensor is the truth, h_true = S2/S0) and of each closure; (bottom) the S0-weighted cell error divided by √(2/3), with the rays' own sampling noise as a grey floor (`tensor_compare.py`'s noise: the distance between the odd- and even-substep h_true, halved). Curves: thin, split, screen, cone (final), and M1 given the rays' flux. | 256³ dumps (13 redshifts, x_V = 0.05–1) | `apps/otvet_tensor` (the code's own tensors: the budget λ of the screen, the final cone with its blend) into `tensor_compare.py --moment`, then `tensor_summary.py` | draft exists (`figures/otvet_closure_apriori.png`, six panels, prototype tensors, final cone at six redshifts only); to remake with the code's tensors at all 13 |
| 6 | The normalisation: A_OTVET/A_true, median N/N_dir and P_Γ(OTVET)/rays against λ_eff/0.61 L, with the line (λ_eff/0.61 L)² | 256³ dumps and runs | from the tables in `otvet_closure.md` §3 | to make (small) |
| **7** | (a) λ_mfp against z with Becker+21 and Zhu+23; (b) τ_eff(84 %) − τ_eff(16 %) over 50 Mpc/h segments, τ rescaled to the Bosman+22 mean flux; every run, full-box snapshots only (user, 2026-11-06) | `data/taueff_mfp_snap_A.txt` (NewRadHydroCode `taueff_z.py --full --norm`) | `scripts/fig_mfp_width.py` | done for the current runs (`figures/fig_mfp_width.pdf`) |
| 8 | 21cmFAST's excursion set on the suite's own density, ζ(z) matched to the rays' x_V: Δ² of x_HII, ratio and r(k) with the rays, beside every method (Figure 2 style), plus a maps column | suite snapshots | `excursion_set.py` / py21cmfast | to make (`prompts/taueff_21cmfast.md`, part B) |
| T1 | Runs, closure keys and cost | `rt_suite_512.md` §3 | — | exists |
| T2 | Closure parameters and defaults | `otvet_closure.md` §5 | — | exists |
| T3 | Γ/⟨Γ⟩ quantiles in ionised cells at z = 5.5 and 5.0 | suite | `gamma_power.py --field gammaHI_avg` | partly (z = 4.99) |

## 4. Decisions

**Decided (user, 2026-11-05):**
- Compare at fixed z.
- Show the case A + RR rays (Figures 2–3).
- No reach test for the cone (`otvet_cone_smax` stays 8).
- No 1024³ cone; the suite's 512³ cone.

**Decided (user, 2026-11-05): no flux-limited diffusion in this paper.**
It is not built (`docs/PLAN.md`, "Thread B", has the plan). The
discussion mentions it with the expected failures (§2, Discussion).

**Decided (user, 2026-11-05): the tensor comparison is in the paper,
from the 256³ runs "for now at least"** (option (a) below, as a two-panel
Figure 5; the configuration stated in one sentence). Option (b) stays
available if the 256³ configuration turns out to matter.

Background: the comparison needs the rays' own Eddington tensor
(`tensor_dump = 1`).
- **The suite** is the 512³ set with one set of parameters, and Figures 1–3
  use it. But none of its runs wrote the tensor, and each kept only its
  last checkpoint, so the dump can't be added by a restart.
- **The earlier 512³ set** (`docs/rt_methods_512.md`, `otvet_closure.md`
  §7: constant 0.2c, f_esc = 0.23, case A + RR) had no tensor dump either.
  Its runs were overwritten by the suite under the same names.
- **The only dumps are the 256³ runs**, which share that earlier set's
  parameters.

The choice:
- (a) the 256³ dumps, stated as a different configuration; or
- (b) a new 512³ ray run with `tensor_dump = 1` in the suite's
  configuration: one serial node for about 24 h, plus disk for the dumps
  at the snapshot steps.

## 5. References

**Read and checked** in `docs/otvet_closure_literature.md` or the
`data/igm` header. Quotes there were captured through a summarising fetch
tool and need checking against the PDFs before quoting.

| reference | used for |
|---|---|
| Wu, McQuinn & Eisenstein 2021, JCAP 02, 042, arXiv:2009.07278 | the OTVET normalisation error, M1's P_Γ suppression, the screened kernel |
| Gnedin & Abel 2001, New Astron. 6, 437, astro-ph/0106278 | OTVET; background term; no shadows |
| Gnedin 2014, ApJ 793, 29, arXiv:1403.4245 (App. C) | CROC's background split |
| Gnedin 2025, arXiv:2504.10571 | CROC vs Thesan transfer functions |
| Gnedin & Katz 2026, OJAp 9, arXiv:2603.22400 (abstract read) | second-order closures unstable, so first-order closures here |
| Finlator, Özel & Davé 2009, MNRAS 393, 1090, arXiv:0808.3578 | attenuated long-characteristics tensor |
| Petkova & Springel 2009, MNRAS 396, 1383, arXiv:0812.1801 | tree OT tensor; shadows fill in |
| Becker et al. 2021, MNRAS, arXiv:2103.16610 | λ_mfp data |
| Zhu et al. 2023, ApJ 955, 115 | λ_mfp data |
| Bosman et al. 2022, MNRAS 514, 55 | ⟨F⟩ data |
| Gaikwad et al. 2023, arXiv:2304.02038 | Γ_HI data |
| Pahl et al. 2025, ApJ 981, 134, arXiv:2407.03399 | ξ_ion = 10^25.38 |
| Tinker et al. 2008, ApJ 688, 709 | halo mass function (abundance matching) |

**Seen only as a search snippet or title; check before citing:**
- Aubert & Teyssier 2008 (ATON), arXiv:0709.1544
- Davis, Stone & Jiang 2012 (short-characteristics VET), arXiv:1201.2223
- Cain & D'Aloisio 2024 (FlexRT), arXiv:2409.04521
- Davies & Furlanetto 2016, arXiv:1509.07131; Davies et al. 2017,
  arXiv:1611.02711 (Γ–λ_mfp coupling)
- Hopkins et al. 2020 (FIRE RT methods, LEBRON), arXiv:1811.12462

**From memory, to look up** (no bibliographic details given here on
purpose):
- **The code and the rays:** Trac & Cen 2007; Trac, Cen & Loeb 2008; Abel
  & Wandelt 2002 (adaptive HEALPix rays); Górski et al. 2005 (HEALPix).
- **M1 and moment codes:** Levermore 1984; Dubroca & Feugeas 1999 and/or
  González et al. 2007; Rosdahl et al. 2013 (RAMSES-RT); Kannan et al.
  2019 (AREPO-RT); Kannan et al. 2022 (Thesan); Ocvirk et al. 2016/2020
  (CoDa).
- **Attenuated sums:** Clark, Glover & Klessen 2012 (TreeCol); Pawlik &
  Schaye 2008 (TRAPHIC); Wünsch et al. 2021 (TreeRay); Crassin et al. 2011
  (voxel cone tracing).
- **Reduced speed of light:** Gnedin 2016; Deparis et al. 2019; Ocvirk et
  al. 2019.
- **Code comparisons:** Iliev et al. 2006, 2009.
- **Setup:** Sheth & Tormen 1999; Eisenstein & Hu 1998; Planck 2018 (τ_es).
- **Late-reionization context (optional):** Kulkarni et al. 2019; Keating
  et al. 2020; Garaldi et al. 2022.

## 6. Work for the threads on klone

- **Figures thread:**
  - Figures 1–3 and Table 3 from the suite.
  - `rt_suite_figures.py`: a `--z` epoch option, a column subset for
    Figure 1, paper styling, PDF output.
  - Confirm f6 and the ĉ schedule from the runs' `params.txt`.
  - Record the commit of every figure.
- **Closure-diagnostics thread:**
  - Check that the `otvcl256` dumps exist.
  - At all 13 dump redshifts, compute each closure's tensor with
    `apps/otvet_tensor` (thin, split, screen with the budget λ, the final
    cone with its blend) and compare it with the rays' using
    `tensor_compare.py --moment` (the M1 curve is `tensor_compare.py`'s
    own: Levermore's D on the rays' flux); make the two-panel Figure 5.
  - Figure 6.
  - The Appendix A table.
  - Not now: the 512³ `tensor_dump` ray run (option (b) in §4).
- **References:** verify the "snippet" and "from memory" entries in a
  session with web access (arXiv and ADS are not reachable from klone),
  and build `refs.bib` here.
- **This repository:** `main.tex`, `refs.bib`, `figures/` (the PDFs),
  and `figures/README` naming the scripts and the NewRadHydroCode commit
  of each figure. No code or data from the private Fortran submodule.
