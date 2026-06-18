# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdda.h

Macro implementation of Bresenham-style digital differential analyzers.

- Used for trapezoid edge tracking, rasterizing transformed images, curve flattening, and potentially lines.
- Represents exact values of `floor(i * D / N)` while maintaining:
  - current quotient `Q`
  - remainder state `R`
  - step values `dQ`, `dR`, `NdR`
- Defines generic DDA state/step macros:
  - `dda_state_struct`
  - `dda_step_struct`
- Provides fixed-point DDA types:
  - `gx_dda_state_fixed`
  - `gx_dda_step_fixed`
  - `gx_dda_fixed`
  - `gx_dda_fixed_point`
- Main operations:
  - `dda_init_state`
  - `dda_init_step`
  - `dda_init`
  - `dda_step_add`
  - `dda_current`
  - `dda_next`
  - `dda_previous`
  - `dda_advance`
  - `dda_translate`
- Handles negative `D` carefully because old C division/remainder semantics were not reliable across compilers.

Important detail: `dda_state_advance` is explicitly noted as inefficient and loops one step at a time.
