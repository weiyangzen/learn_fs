# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctred.c

Reduced-size inverse DCT routines, compiled under `IDCT_SCALING_SUPPORTED`. The file implements 8x8 coefficient block decoding directly to 4x4, 2x2, or 1x1 output.

Exports:

- `jpeg_idct_4x4()`
- `jpeg_idct_2x2()`
- `jpeg_idct_1x1()`

The 4x4 and 2x2 routines derive reduced outputs from simplified LL&M IDCT steps, skipping columns and coefficients that cannot affect the smaller output. They use the same fixed-point scaling style as `jidctint.c`, with zero-AC shortcuts and range-limited output. The 1x1 path is just the dequantized DC coefficient divided by 8.
