# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcoord.h

Internal graphics-state coordinate transformation declarations.

Key contents:
- Declares `gx_translate_to_fixed` for fixed-point translation and existing path translation.
- Declares `gx_scale_char_matrix` for CTM and character matrix oversampling.
- Declares `gx_matrix_to_fixed_coeff` for deriving fast fixed-point distance-transform coefficients from a matrix.

Notable dependencies:
- Requires graphics coordinate/matrix state definitions through `gscoord.h`.

Research notes:
- This is a small internal API header; implementations live elsewhere.
- It is used by character/path rendering code that needs fixed-point CTM support.
