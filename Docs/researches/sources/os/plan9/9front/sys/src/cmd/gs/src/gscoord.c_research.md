# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.c

## Role

`gscoord.c` implements Ghostscript coordinate-system and current transformation matrix (CTM) operations, including default matrix handling, text character matrices, transforms, inverse transforms, and fixed-point transform helpers.

This is graphics-state geometry infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_initmatrix`
- `gs_defaultmatrix`
- `gs_setdefaultmatrix`
- `gs_currentmatrix`
- `gs_setcharmatrix`
- `gs_currentcharmatrix`
- `gs_setmatrix`
- `gs_imager_setmatrix`
- `gs_settocharmatrix`
- `gs_translate`
- `gs_scale`
- `gs_rotate`
- `gs_concat`
- `gs_transform`
- `gs_dtransform`
- `gs_itransform`
- `gs_idtransform`
- `gs_imager_idtransform`
- `gx_translate_to_fixed`
- `gx_scale_char_matrix`
- `gx_matrix_to_fixed_coeff`
- `fixed_coeff_mult`

## Core Behavior

The file updates CTM state and invalidates cached inverse CTM and cached character matrix whenever transforms change.

`gs_defaultmatrix` uses the current device’s initial matrix, then applies device margins scaled by hardware resolution, unless an explicit default matrix has been set.

`gs_setcharmatrix` composes a font matrix with the CTM and caches a fixed-point-capable character matrix.

Inverse transform functions prefer exact inverse operations for non-skewed matrices and use cached inverse matrices only for skewed cases.

`gx_translate_to_fixed` adjusts CTM translation to exact fixed coordinates and translates the current path by the corresponding fixed delta when possible.

`gx_matrix_to_fixed_coeff` and `fixed_coeff_mult` prepare and use fixed-point coefficients for fast distance transformations while avoiding overflow.

## Precision Design

`ROUND_CTM_FIXED` aligns floating CTM translation values with rounded fixed translations to avoid anomalies such as `0 0 moveto currentpoint` not returning exactly `0 0`.

## Dependencies

Uses matrix, fixed-point arithmetic, path translation, device initial matrix, font matrix, and graphics/imager state internals.

## Notable Risks

- Large or fractional path translations fail with `limitcheck` when fixed CTM translation is invalid and the path is non-null.
- Cached inverse and character matrices depend on consistent invalidation.
- Fixed coefficient scaling uses bit-width assumptions and must avoid overflow across supported architectures.
