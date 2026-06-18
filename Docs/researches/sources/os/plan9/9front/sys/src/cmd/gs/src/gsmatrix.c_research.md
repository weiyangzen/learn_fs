# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.c

Implements matrix creation, arithmetic, coordinate transforms, fixed-point transforms, and compact stream serialization.

Key behavior:
- Provides identity, translation, scaling, and degree-based rotation matrix constructors.
- `gs_matrix_multiply` optimizes for matrices with zero off-diagonal entries.
- `gs_matrix_invert` handles diagonal and general matrices, returning `undefinedresult` for singular matrices.
- Translate/scale/rotate support in-place operation.
- Point and distance transforms have fast paths for diagonal and swapped-axis matrices.
- Bounding-box transforms convert all four corners and recompute min/max to handle rotations and rounding consistency.
- `gs_matrix_fixed_from_matrix` copies a float matrix into fixed-matrix form and caches fixed translation when in range.
- Fixed-point point/distance transform functions use checked fixed multiply/sum helpers and return `limitcheck` on overflow.
- Optional precise currentpoint path uses rounded fixed conversion.
- `sput_matrix` serializes matrices compactly with a control byte and only nonzero/nonredundant float coefficients.
- `sget_matrix` decodes that representation from a stream.

Dependencies:
- Uses `gxmatrix.h`, `gxfixed.h`, `gxfarith.h`, and `stream.h`.
- Uses trig helpers from `gsmisc.c` via `gs_sincos_degrees`.

Research notes:
- The matrix stream representation is private to this file.
- Fixed-point conversion is performance-sensitive and heavily guarded for overflow.
