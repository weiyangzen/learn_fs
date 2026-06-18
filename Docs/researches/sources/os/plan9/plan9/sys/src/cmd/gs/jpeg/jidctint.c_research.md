# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctint.c

Slow-but-accurate integer inverse DCT implementation, compiled under `DCT_ISLOW_SUPPORTED`. It is the integer IDCT counterpart to `jfdctint.c`, using the LL&M algorithm and fixed-point constants at `CONST_BITS == 13`.

The exported `jpeg_idct_islow()` dequantizes coefficients with the component `ISLOW_MULT_TYPE` table, runs a column pass into an integer workspace, then a row pass into the destination sample buffer. It preserves precision with `PASS1_BITS` and delayed descaling.

The implementation optimizes all-zero AC columns by replicating the DC value, and optionally optimizes all-zero AC rows. Output samples are descaled by the total IDCT scale factor and clipped through the decompressor range-limit table.
