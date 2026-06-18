# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jidctred.c

Purpose: reduced-size inverse DCT routines for scaled decompression.

Exports:
- `jpeg_idct_4x4()`
- `jpeg_idct_2x2()`
- `jpeg_idct_1x1()`

Important behavior:
- Compiled only when `IDCT_SCALING_SUPPORTED` is enabled.
- Decodes an 8x8 coefficient block directly to 4x4, 2x2, or 1x1 output.
- The 4x4 and 2x2 routines use simplified LL&M IDCT steps.
- Skips columns and coefficients that cannot affect the smaller output.
- Uses fixed-point scaling, zero-AC shortcuts, and range-limited output.
- The 1x1 path computes only the dequantized DC coefficient divided by 8.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, decompressor DCT tables.
