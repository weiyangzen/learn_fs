# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfarith.h

Floating-point arithmetic support macros and trig declarations.

- Includes `gconfigv.h` for `USE_FPU` and `gxarith.h`.
- On systems with no/slow FPU and IEEE floats, overrides selected float-test macros with bit-level tests:
  - `is_fzero`
  - `is_fzero2`
  - `is_fneg`
  - `is_fge1`
  - `f_fits_in_ubits`
  - `f_fits_in_bits`
- Handles float-as-int access depending on architecture word size.
- Handles sign-byte detection depending on endian.
- Defines IEEE constants:
  - `IEEE_expt`
  - `IEEE_f1`
- Declares degree-based trig helpers:
  - `gs_sin_degrees`
  - `gs_cos_degrees`
  - `gs_sincos_degrees`
- Defines `gs_sincos_t`, including an `orthogonal` flag for multiples of 90 degrees.
- Declares `gs_atan2_degrees`, which follows PostScript quadrant rules and may return `gs_error_undefinedresult`.

Risk note: the slow-FPU path uses type-punning through pointer casts, reflecting old Ghostscript portability assumptions.
