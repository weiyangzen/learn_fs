# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmatrix.c

## Purpose
Implements PostScript matrix and coordinate transformation operators.

## Key Functions
- `zinitmatrix()`, `zdefaultmatrix()`, `zcurrentmatrix()`, `zsetmatrix()`, and `zsetdefaultmatrix()` expose CTM/default matrix operations.
- `ztranslate()`, `zscale()`, and `zrotate()` operate either on the graphics state or produce a matrix when a matrix operand is supplied.
- `zconcat()`, `zconcatmatrix()`, and `zinvertmatrix()` perform matrix composition/inversion.
- `ztransform()`, `zdtransform()`, `zitransform()`, and `zidtransform()` share `common_transform()`.

## Important Behavior
- Transform operators optimize the common no-matrix case.
- Matrix-producing forms overwrite operands to match PostScript stack results.
- `common_transform()` accepts normal arrays and packed arrays as possible matrix operands.
- Default matrix can be reset with `null`.

## Research Notes
Bridge from PostScript matrix syntax to Ghostscript `gsmatrix` and coordinate APIs.
