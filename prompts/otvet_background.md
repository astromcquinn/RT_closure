# Thread prompt (cloud session with arXiv allowed, then klone): OTVET with the isotropic background of Gnedin & Abel (2001) and CROC

*Written 2026-11-07. Paste everything below the line into a Claude Code
session in a checkout of `astromcquinn/NewRadHydroCode`. The design and
implementation need arXiv (the two papers); the validation runs are on
klone.*

---

Read CLAUDE.md, docs/STATUS.md, docs/rt_moments.md, docs/otvet_closure.md
(§2, §4, §5) and docs/otvet_closure_literature.md §1 and §3, then
src/rt_moments.cpp, include/radray/kernels/moment_cell.hpp,
src/otvet_closure.cpp and include/radray/otvet_closure.hpp. Branch
`otvet-background` off `main`; commit often and push; one PR at the end.
Do not run anything at 512^3 without the user's go-ahead.

Goal: an OTVET closure with the isotropic background component of the
original scheme, so the paper can compare against OTVET as Gnedin & Abel
(2001, astro-ph/0106278) and CROC (Gnedin 2014, arXiv:1403.4245, App. C)
use it. Our `rt_method = otvet` applies the optically thin tensor h to the
whole radiation field. Both papers apply it only to a local part and carry
the rest as an isotropic background:
- Gnedin & Abel 2001, their eq. 4 and eq. 17: the mean intensity J-bar
  evolves with the box-mean emissivity and a radiation-weighted mean
  absorption. The relative field is split into E1 (isotropic tensor,
  sourced by Lambda times the mean emissivity) and D2 (thin tensor,
  sourced by rho* - rho*-bar Lambda), with
  Lambda = exp(-<kappa> L) and L = (1/4 pi) Int d^3x / r^2 over the box.
  Their eq. 16 was abandoned because the local field changed sign; read
  why.
- CROC (Gnedin 2014, eqs. C2-C11): J = J-bar f + L (g - g-bar f). J-bar is
  the mean intensity, its Lyman-limit absorption taken from observations
  (Songaila & Cowie 2010), not from the box. g is the box sources' light
  (thin tensor, eq. C10). f is the background's local modulation
  (isotropic tensor, eq. C11, stabilised with q(f-bar) = 2/f-bar - 1).
Download both papers from arXiv and read these sections in full. Quote
equation numbers in the design; do not reconstruct them from memory.

Step 1, design (stop and ask the user before implementing): write
docs/otvet_background.md with
- how each scheme maps onto our explicit two-moment GLF solver (N, F per
  frequency group, D N in the flux equation, photons per mean H atom,
  absorption through photo_cell's fgam scaling, the reduced speed of
  light c-hat, redshifting per distance);
- the candidate formulations, with their costs:
  (a) G&A-like: two moment fields per group, background with D = I/3 and
      local with D = h, the Lambda split of the sources, Lambda from a
      global mean opacity (from the box) or a fixed mean free path;
  (b) CROC-like: a global mean intensity (an ODE per group, with a mean
      free path that is either observed or a parameter) plus a local
      modulation field, and the local sources' field with the thin
      tensor and its box mean subtracted;
  (c) anything simpler that reproduces their limits (Lambda -> 0: pure
      OTVET; Lambda -> 1: the mean emission isotropic);
- for each: positivity (the GLF update must stay positive: can a field go
  negative?), photon conservation (the ray.log budget must close to
  float precision), how the background is absorbed in dense or shielded
  gas, memory (one more N, F, E per group?), and how it differs from our
  existing `otvet_split` (which takes the isotropic share cell by cell
  from N - N_OT with no lambda) and `otvet_closure = screen`.
Recommend one formulation and say what the user must decide (the mean
free path source in particular: from the box, fixed, or tied to
observations).

Step 2, after the user's decision: implement behind a new key (e.g.
`otvet_background = none | ga01 | croc`, default none, and
byte-identical to now: check radhydro smoke and rt_driver lognormal_16src
against main with compare.py --rtol 0 --atol-frac 0). Deterministic and
independent of the thread count. Tests in test_moments (positivity,
photon conservation, the Lambda -> 0 limit equal to pure OTVET bitwise,
a uniform-emissivity box where the background must be isotropic), thread
tests and a restart test like the existing otvet_split ones; the fast
suite must pass.

Step 3, validation at 256^3 (klone; the user runs it or gives the
go-ahead): the configuration of the otvcl256 runs (docs/otvet_closure.md
§1, §6), the new closure against the rays, thin OTVET, the split and the
cone: apps/otvet_tensor on the rays' tensor dumps (a priori: block
anisotropy and cell error against z, as in docs/otvet_closure.md §3),
then a full run with gamma_power.py, rt_methods_runs.py and reion_power.py.
Report in docs/otvet_background.md; update docs/STATUS.md and PLAN.md.
