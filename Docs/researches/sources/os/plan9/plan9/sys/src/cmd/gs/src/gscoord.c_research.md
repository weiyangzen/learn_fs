# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.c

## Purpose
Implements Ghostscript coordinate-system and CTM operators.

## Key Behavior
- Maintains CTM, fixed CTM translation, CTM inverse validity, and character-matrix validity.
- Implements:
  - `gs_initmatrix`,
  - `gs_defaultmatrix`,
  - `gs_setdefaultmatrix`,
  - `gs_currentmatrix`,
  - `gs_setmatrix`,
  - `gs_translate`,
  - `gs_scale`,
  - `gs_rotate`,
  - `gs_concat`.
- Implements character matrix routines:
  - `gs_setcharmatrix`,
  - `gs_currentcharmatrix`,
  - `gs_settocharmatrix`.
- Implements forward and inverse point/distance transforms.
- Provides internal helpers:
  - `gx_translate_to_fixed`,
  - `gx_scale_char_matrix`,
  - `gx_matrix_to_fixed_coeff`,
  - `fixed_coeff_mult`.

## Important Details
- `ROUND_CTM_FIXED` adjusts floating translation to exactly match rounded fixed translation, avoiding anomalies such as `0 0 moveto currentpoint` not returning `0 0`.
- Inverse transforms use exact inverse formulas for non-skewed matrices rather than cached inverse matrices for better accuracy.
- `gx_translate_to_fixed` translates the current path when CTM fixed translation is valid; otherwise a nonempty path triggers `limitcheck`.
- `gx_matrix_to_fixed_coeff` chooses scaling to prevent overflow in fixed-point distance transforms.

## Dependencies
Uses matrix math, fixed arithmetic, path translation, graphics-state internals, font character matrices, devices for default matrix, and debug tracing.

## Research Notes
This is core rendering state machinery. Its main risk surface is numerical precision and invalidation correctness for CTM inverse and character matrices.
