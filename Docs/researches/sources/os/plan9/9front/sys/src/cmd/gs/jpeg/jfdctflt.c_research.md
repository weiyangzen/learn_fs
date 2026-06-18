# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jfdctflt.c

Purpose: floating-point forward DCT implementation for compression.

Key routine:
- `jpeg_fdct_float(FAST_FLOAT *data)` performs an in-place 8x8 forward DCT using two 1-D passes.

Important behavior:
- Compiled only when `DCT_FLOAT_SUPPORTED` is enabled.
- Enforces `DCTSIZE == 8` with a deliberate syntax error otherwise.
- Uses the Arai, Agui, and Nakajima scaled DCT algorithm.
- Processes rows first, then columns.
- Uses constants including `0.707106781`, `0.382683433`, `0.541196100`, and `1.306562965`.
- Produces scaled DCT coefficients for later quantization by the compression DCT manager.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, `FAST_FLOAT`.

Notes:
- This is compression-side code, despite being adjacent to decompression IDCT implementations.
