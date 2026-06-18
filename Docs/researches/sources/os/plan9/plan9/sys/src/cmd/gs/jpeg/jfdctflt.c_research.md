# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctflt.c

Purpose: floating-point forward DCT implementation.

Key routine:
- `jpeg_fdct_float(FAST_FLOAT *data)` performs an in-place 8x8 forward DCT using two 1-D passes.

Important behavior:
- Compiled only when `DCT_FLOAT_SUPPORTED` is enabled.
- Enforces `DCTSIZE == 8` with a deliberate syntax error otherwise.
- Uses the Arai, Agui, and Nakajima scaled DCT algorithm.
- Processes rows first, then columns, with five key multiplies per 1-D DCT and constants such as `0.707106781`, `0.382683433`, `0.541196100`, and `1.306562965`.
- Produces scaled DCT coefficients for later quantization by the compression DCT manager.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, `FAST_FLOAT`.

Notes:
- Although grouped with decompression files, this is compression-side forward DCT code in the same JPEG module directory.
