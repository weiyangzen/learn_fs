# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jidctint.c

Purpose: slow-but-accurate integer inverse DCT implementation.

Key routine:
- `jpeg_idct_islow()` dequantizes coefficients and performs IDCT for one 8x8 block.

Important behavior:
- Compiled only when `DCT_ISLOW_SUPPORTED` is enabled.
- Integer IDCT counterpart to `jfdctint.c`.
- Uses the LL&M fixed-point algorithm with `CONST_BITS == 13`.
- Dequantizes coefficients with the component `ISLOW_MULT_TYPE` table.
- Runs a column pass into an integer workspace, then a row pass into the destination sample buffer.
- Preserves precision with `PASS1_BITS` and delayed descaling.
- Optimizes all-zero AC columns by replicating the DC value.
- Optionally optimizes all-zero AC rows.
- Output samples are clipped through the decompressor range-limit table.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`.
