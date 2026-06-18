# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctflt.c

Floating-point inverse DCT implementation, compiled under `DCT_FLOAT_SUPPORTED`. It is specialized to 8x8 DCT blocks and combines dequantization with IDCT.

The exported `jpeg_idct_float()` uses the Arai/Agui/Nakajima scaled DCT algorithm. It multiplies coefficients by the component floating-point multiplier table, runs a column pass into a local `FAST_FLOAT workspace[DCTSIZE2]`, then runs a row pass into the output sample buffer.

Column processing has a shortcut for all-zero AC terms, filling the workspace column with the dequantized DC value. Final row outputs are descaled by 8 and clipped through `IDCT_range_limit(cinfo)`.
