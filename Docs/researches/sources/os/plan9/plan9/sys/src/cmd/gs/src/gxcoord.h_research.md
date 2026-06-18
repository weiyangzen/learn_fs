# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcoord.h

## Purpose
Declares internal graphics-state coordinate transformation helpers.

## Public Surface
- `gx_translate_to_fixed(gs_state *, fixed, fixed)`: sets translation to a fixed-point value and translates any current path.
- `gx_scale_char_matrix(gs_state *, int, int)`: scales CTM and character matrix for oversampling.
- `gx_matrix_to_fixed_coeff(const gs_matrix *, fixed_coeff *, int)`: computes fixed-point distance transformation coefficients from a matrix.

## Dependencies
Requires public coordinate APIs plus internal matrix/state definitions supplied by including context.

## Risks and Notes
- This is declaration-only; behavior is implemented elsewhere.
- Callers use these helpers where fixed-point precision and character oversampling matter.

Filesystem relevance: none. It is graphics coordinate infrastructure.
