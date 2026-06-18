# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitcom.c

Purpose: Oversampled bitmap-to-alpha compression.

Key behavior: `bits_compress_scaled` compresses an X-by-Y oversampled 1-bit bitmap into 1-, 2-, or 4-bit alpha pixels by counting set bits in each source cell and mapping counts through precomputed compression tables.

Optimization and quality: Fast paths handle all-zero and all-one input bytes when alignment permits. For low but nonzero coverage that would compress to zero, it samples adjacent vertical and horizontal cells using leading/trailing bit-count tables to reduce dropout artifacts.

Parameters: Supports independent X/Y scale factors of 1, 2, or 4 via `gs_log2_scale_point`, source x bit offset, source/destination rasters, and optional `ALPHA_LSB_FIRST` nibble ordering.

Dependencies and notes: Uses bit-count lookup tables and debug channel `B`. Width, height, and source x are expected to align with the oversampling factors.
