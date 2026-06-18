# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jidctflt.c

Purpose: floating-point inverse DCT implementation for decompression.

Key routine:
- `jpeg_idct_float()` combines dequantization with IDCT for one 8x8 coefficient block.

Important behavior:
- Compiled only when `DCT_FLOAT_SUPPORTED` is enabled.
- Specialized to 8x8 DCT blocks.
- Uses the Arai, Agui, and Nakajima scaled DCT algorithm.
- Multiplies coefficients by the component floating-point multiplier table.
- Runs a column pass into local `FAST_FLOAT workspace[DCTSIZE2]`, then a row pass into the output sample buffer.
- Has a column all-zero AC shortcut that fills the workspace column with the dequantized DC value.
- Final row outputs are descaled by 8 and clipped through `IDCT_range_limit(cinfo)`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, decompressor component DCT tables.
