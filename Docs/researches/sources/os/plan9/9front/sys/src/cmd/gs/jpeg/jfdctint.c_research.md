# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jfdctint.c

Purpose: slow-but-accurate integer forward DCT implementation.

Key routine:
- `jpeg_fdct_islow(DCTELEM *data)` performs an in-place 8x8 forward DCT.

Important behavior:
- Compiled only when `DCT_ISLOW_SUPPORTED` is enabled.
- Specialized to `DCTSIZE == 8`; otherwise intentionally fails compilation.
- Uses the Loeffler, Ligtenberg, and Moschytz alternate method with fixed-point arithmetic.
- Processes rows first, then columns.
- Leaves final results scaled by IJG convention so later quantization removes the remaining factor of 8.

Key definitions:
- `CONST_BITS == 13` fixed-point constants.
- `PASS1_BITS` depends on sample precision.
- Uses `MULTIPLY16C16` for 8-bit builds.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`.

Notes:
- Arithmetic is arranged to avoid multiple multiplications on one data path and keep 32-bit intermediates bounded.
