# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctfst.c

Purpose: fast, lower-accuracy integer forward DCT implementation.

Key definitions and routine:
- `CONST_BITS = 8`.
- Precomputed AA&N constants: `FIX_0_382683433`, `FIX_0_541196100`, `FIX_0_707106781`, `FIX_1_306562965`.
- Optional inaccurate rounding override for speed when `USE_ACCURATE_ROUNDING` is not defined.
- `MULTIPLY(var,const)` multiplies and descales immediately.
- `jpeg_fdct_ifast(DCTELEM *data)` performs an in-place 8x8 two-pass forward DCT.

Important behavior:
- Compiled only when `DCT_IFAST_SUPPORTED` is enabled.
- Enforces `DCTSIZE == 8` with a deliberate syntax error otherwise.
- Uses the Arai, Agui, and Nakajima scaled DCT algorithm.
- Trades precision for fewer shifts, smaller fixed-point constants, and faster 16-bit-friendly intermediates.
- Intended to pair with quantization tables adjusted for the scaled DCT convention.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, fixed-point macros and `DCTELEM`.

Notes:
- This is compression-side DCT support included in the same vendored JPEG code batch.
