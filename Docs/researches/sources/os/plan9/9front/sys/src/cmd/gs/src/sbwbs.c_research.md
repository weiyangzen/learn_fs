# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.c

Implements Burrows-Wheeler block sort encode/decode filters and a shared buffered-block stream helper. The common helper allocates a block buffer, fills it from input, flips between filling and draining modes, and frees storage on release.

Encoding reverses the buffered block, sorts all cyclic rotations using an initial radix bucket pass plus `qsort`, writes block length and original index, and emits the transformed last-column bytes. Decoding reads length/index, fills the transformed block, builds inverse permutation offset tables, then reconstructs output bytes through LF-mapping.

The decoder uses `SHORT_OFFSETS` tables to reduce memory: 64K-level full offsets, 4K-level 16-bit offsets, and packed 12-bit per-entry residual offsets. It falls back to an int offset table if that macro is disabled.

Dependencies include Ghostscript memory/stream code, `qsort`, and `sbwbs.h`.

Risk notes: the encoder uses a static global pointer to pass stream state into the comparison callback, so concurrent sorting in multiple streams would not be reentrant. This is compression filter code, not filesystem code.
