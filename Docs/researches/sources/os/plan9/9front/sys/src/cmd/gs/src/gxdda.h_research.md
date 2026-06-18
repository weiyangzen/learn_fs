# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdda.h

This header implements macro-based Bresenham-style digital differential analyzers used by Ghostscript for trapezoid edges, rotated/skewed image coordinates, curve subdivision, and potentially single-pixel lines. It assumes `gxfixed.h` has supplied fixed-point types.

The comment describes the invariant used to compute exact `floor(i * D / N)` values without letting the remainder leave range. `dda_state_struct` and `dda_step_struct` define state and step layouts; `gx_dda_fixed` combines fixed-point current value `Q` with unsigned remainder `R` and per-step `dQ`, `dR`, `NdR`.

The macro API initializes state and steps (`dda_init_state`, `dda_init_step`, `dda_init`), adds steps (`dda_step_add`), reads the current value (`dda_current`, `dda_current_fixed2int`), steps forward/backward (`dda_next`, `dda_previous`), advances by repeated stepping, and translates the current position.

The implementation explicitly handles negative `D` without depending on compiler-specific signed division/remainder behavior. `dda_advance` is noted as inefficient because it loops one step at a time for the fractional remainder.

Filesystem relevance: none. This is scan-conversion arithmetic for rendering.
