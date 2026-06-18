# File Research: sources/virtualization/spdk/lib/util/xor.c

This file implements XOR parity generation across multiple source buffers.

`spdk_xor_gen()` validates source count `2 <= n <= 256`, then delegates to an optimized or basic implementation. The basic path uses 64-bit word XOR when destination and all sources are aligned to `sizeof(uint64_t)`, and byte-wise XOR otherwise. Any tail bytes after the word-aligned portion are processed byte-wise.

When SPDK is built with ISA-L, `do_xor_gen()` uses ISA-L `xor_gen()` when all buffers meet 32-byte alignment; otherwise it falls back to the basic implementation. `spdk_xor_get_optimal_alignment()` returns 32 with ISA-L or `sizeof(uint64_t)` without it.

Important constraints are the maximum source count of 256, alignment-sensitive acceleration, and caller responsibility for valid non-overlapping or otherwise safe buffers.
