# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.h

Public matrix type and matrix API declarations.

Key definitions:
- `gs_matrix` has six PostScript matrix coefficients: `xx`, `xy`, `yx`, `yy`, `tx`, `ty`.
- `constant_matrix_body` and `identity_matrix_body` support static initialization.
- `is_xxyy` and `is_xyyx` detect diagonal or swapped-axis simple matrices for fast paths.

Key declarations:
- Matrix creation, multiply/invert/translate/scale/rotate.
- Point, distance, and bbox transforms, including inverse variants.
- Stream serialization: `sget_matrix`, `sput_matrix`.

Research notes:
- This header is the public client interface; fixed-matrix details live in internal headers and `gsmatrix.c`.
