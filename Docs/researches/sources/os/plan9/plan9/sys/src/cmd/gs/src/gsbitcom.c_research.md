# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitcom.c

Purpose: Compresses oversampled 1-bit bitmaps into lower-resolution alpha maps by counting set bits.

Key interface: `bits_compress_scaled`.

Control flow: lookup tables count half-byte bits, edge-adjacent bits, and map counts from oversampling factors to 1/2/4-bit alpha values. The main loop walks scaled source cells, fast-paths all-zero and all-one aligned source bytes, otherwise counts set bits over X/Y oversampling cells, optionally adds adjacent-cell evidence to reduce dropouts, clamps to maximum count, and packs alpha output.

Dependencies: Uses `gs_log2_scale_point`, `gsbitops.h`, debug logging, byte-oriented bitmap layout, and optional `ALPHA_LSB_FIRST`.

Risks and notes: Supports X/Y scale factors 1, 2, or 4 and output bits 1, 2, or 4. In-place compression is only safe when output bits do not exceed X oversampling. Comments note LSB-first mode is specialized and does not interact well with the rest of the code.
