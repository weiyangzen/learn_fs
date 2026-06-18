# sources/test-tools/fio/crc/xxhash.c

Purpose: Vendor-style implementation of 32-bit xxHash for fast, deterministic, non-cryptographic hashing inside fio.

Important APIs/functions: Implements `XXH32()`, `XXH32_init()`, `XXH32_update()`, `XXH32_digest()`, `XXH32_intermediateDigest()`, `XXH32_sizeofState()`, and `XXH32_resetState()`. Internal helpers cover endian detection, unaligned reads, byte swapping, rotations, the block mixing loop, and final avalanche.

Control flow: One-shot `XXH32()` dispatches to `XXH32_endian_align()` with endianness and alignment policy. Streaming mode allocates or accepts a `struct XXH_state32_t`, initializes accumulators from the seed, buffers less than 16 bytes in `memory`, mixes 16-byte stripes into four lanes, and finalizes by folding lanes plus remaining 4-byte and 1-byte tails. `XXH32_digest()` computes the intermediate digest and frees heap state created by `XXH32_init()`.

State/persistence: Streaming state holds total length, seed, four accumulators, a small tail buffer, and `memsize`. Heap allocation is used only by `XXH32_init()`; static allocation is supported through the header state-space API.

Dependencies/integration: Includes `xxhash.h`, `stdlib.h`, and `string.h`. Used by fio's hash/checksum paths and the CRC benchmark.

Risks: `XXH32_init()` does not check `malloc()` before resetting state. Update length is signed `int`; negative values would corrupt `total_len` and pointer arithmetic if misused. Optional null-input handling is disabled, so null pointers with nonzero length fault. Some unaligned/aligned compile-time branches are subtle and architecture-sensitive.

Test signals: SMHasher-style vectors, one-shot versus streaming equivalence across chunk boundaries, endian cross-checks, and state-space allocation tests provide confidence. Fio `crc/test.c` exercises performance only.
