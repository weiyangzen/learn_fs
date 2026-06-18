<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/arm64/crc32-arm64.c -->
# sources/storage-engines/wiredtiger/src/checksum/arm64/crc32-arm64.c

## Purpose
Provides the ARM64 CRC32C dispatch implementation. On Linux builds with hardware CRC enabled, it detects `HWCAP_CRC32` and returns functions that use ARM CRC32 instructions; otherwise it returns WiredTiger's software CRC32C routines.

## Important APIs, Types, and Functions
The exported symbols are `wiredtiger_crc32c_func(void)` and `wiredtiger_crc32c_with_seed_func(void)`, both declared with default visibility under GCC. Hardware helpers are `__checksum_hw` and `__checksum_with_seed_hw`. Inline assembly macros `CRC32CX`, `CRC32CW`, `CRC32CH`, and `CRC32CB` issue 64-bit, 32-bit, 16-bit, and 8-bit ARM CRC32C instructions. External fallbacks are `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`.

## Control Flow
`wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func` cache the chosen function pointer in a static local. On first call they read `getauxval(AT_HWCAP)` and choose the hardware helper only when `HWCAP_CRC32` is present. The hardware seeded helper starts with `~seed`, processes two 64-bit words per loop with `memcpy` loads, then handles remaining 8-, 4-, 2-, and 1-byte fragments according to the remaining length bits, and returns the complemented CRC. The unseeded helper calls the seeded helper with seed zero.

## State and Persistence Behavior
The only state is the process-local cached function pointer. There is no persistence, allocation, or WiredTiger session state. The function choice affects all block/page checksum persistence indirectly because callers use the returned CRC32C function when writing and validating on-disk checksums.

## Dependencies and Integration Points
This file depends on `wiredtiger_config.h`, Linux `getauxval`, `asm/hwcap.h`, compiler inline assembly support, and the software checksum implementation. It integrates with the global checksum API used by block writes, block reads, disaggregated page checks, examples, and tests through `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`.

## Risks and Edge Cases
Hardware dispatch is Linux-only and can be disabled with `HAVE_NO_CRC32_HARDWARE`. The static pointer cache is intentionally unsynchronized; concurrent first calls may repeat detection but should converge on the same function. `memcpy` avoids unaligned-load undefined behavior. Correctness depends on seed complement semantics matching software and other architecture implementations. Zero-length seeded calls must return the seed.

## Test Signals
`test/catch2/misc_tests/test_crc32.cpp` verifies zero-length and seeded behavior plus known CRC values and chunked seeded computation. `test/csuite/wt2695_checksum/main.c` compares hardware dispatch against `__wt_checksum_sw` across known strings, all-zero/all-0xff data, random data, cumulative chunking, and misalignment cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/arm64/crc32-arm64.c -->
