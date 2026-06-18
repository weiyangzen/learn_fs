<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/vec_crc32.c -->
# sources/storage-engines/wiredtiger/src/checksum/power8/vec_crc32.c

## Purpose
Implements the POWER8 hardware-accelerated CRC32C algorithm using AltiVec/crypto vector builtins and the generated constants in `crc32_constants.h`. It handles unaligned prefixes/tails in scalar code, folds aligned data in vector lanes, and performs final Barrett reduction.

## Important APIs, Types, and Functions
The exported function is `crc32_vpmsum(unsigned int crc, const unsigned char *p, unsigned long len)`. Private helpers include scalar `crc32_align` and aligned vector reducer `__crc32_vpmsum`. Important macros/constants include `VMX_ALIGN`, `VMX_ALIGN_MASK`, `POWER8_INTRINSICS`, `CRC_TABLE`, `GROUP_ENDING_NOP`, `BYTESWAP_DATA`, `VEC_PERM`, and the included `crc_table`, `vcrc_const`, `vcrc_short_const`, and `v_Barrett_const`.

## Control Flow
`crc32_vpmsum` applies the optional initial XOR, uses `crc32_align` for small inputs or unaligned prefixes, calls `__crc32_vpmsum` for the aligned 16-byte multiple, handles the remaining tail with `crc32_align`, then applies the final XOR. `__crc32_vpmsum` has a short path for inputs under 256 bytes that uses `vcrc_short_const`, and a long path that processes data in up to `MAX_SIZE` blocks, folding eight parallel 128-bit chunks to mask vpmsum latency. After long-block processing it reduces tail data, xors parallel lanes together, and performs reflected Barrett reduction to a 32-bit CRC result.

## State and Persistence Behavior
The implementation is stateless. It directly determines CRC32C values stored in WiredTiger block headers and address cookies on POWER8 hardware builds. Seeded operation is provided by passing the prior CRC into `crc32_vpmsum`, so chunked checksums must equal one-shot checksums.

## Dependencies and Integration Points
This file compiles only for `__powerpc64__` when hardware CRC is enabled. It depends on `altivec.h`, compiler vector crypto builtins, `crc32_constants.h`, and `clang_workaround.h` for Clang. `crc32_wrapper.c` exposes it through `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`.

## Risks and Edge Cases
The algorithm is sensitive to alignment, endian/reflection handling, vector lane ordering, and polynomial constants. The scalar prefix/tail path must match vector folding exactly. The long loop uses modulo scheduling and `GROUP_ENDING_NOP` to avoid POWER8 load-hit-store dispatch penalties; compiler changes can affect generated code. Inputs around 0, 1-15 bytes, 16-byte alignment boundaries, 128/256-byte thresholds, and `MAX_SIZE` block boundaries are important edge cases.

## Test Signals
`wt2695_checksum` is the key regression signal because it compares hardware/vector and software CRC values for fixed vectors, all-zero/all-ones inputs, random power-of-two and random sizes, cumulative seeded chunks, and every small length/misalignment combination under 16 bytes. `test_crc32.cpp` verifies zero-length seeded semantics, known CRC32C values, and chunked computation through the dispatch wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/vec_crc32.c -->
