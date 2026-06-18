# sources/storage-engines/wiredtiger/src/checksum/software/checksum.c

## Purpose
This file is the portable CRC32C implementation used whenever a hardware backend is unavailable or disabled. It implements the slicing-by-8 algorithm over static CRC tables, with separate table material for big-endian and little-endian builds so all platforms return the same external checksum value.

## Important APIs, Types, and Functions
`g_crc_slicing[8][256]` is the static lookup table used by the slicing algorithm. `__wt_checksum_with_seed_sw(uint32_t seed, const void *chunk, size_t len)` is the main software entry point and supports cumulative CRC calculation by starting from a caller-provided seed. `__wt_checksum_sw(const void *chunk, size_t len)` is the zero-seed wrapper used by architecture dispatchers.

## Control Flow
The seeded function initializes `crc` to `~seed`, consumes leading bytes until the pointer reaches a 4-byte boundary, processes the bulk of the buffer as pairs of 32-bit words inside an 8-byte loop, then handles trailing bytes. The big-endian branch uses byte-reversed tables and a final byte swap so the result matches little-endian output. The non-seeded wrapper delegates directly to the seeded implementation with seed zero.

## State and Persistence
The implementation has no mutable global state and persists nothing. Its only state is the static table and local CRC accumulator. Checksum stability is persistence-critical indirectly because block, log, and metadata readers compare stored checksum fields against values produced through the process-global checksum function pointer.

## Dependencies and Integration Points
The file depends on `wiredtiger_config.h` for endian feature macros and on fixed-width integer types. Architecture-specific wrappers declare these functions and use them as fallback targets. `src/support/global.c` installs the selected checksum functions into `__wt_process.checksum` and `__wt_process.checksum_with_seed`, which are used through `__wt_checksum` macros by block, log, disaggregated block, eviction, salvage, and diagnostic paths.

## Risks and Edge Cases
Correctness depends on exact table constants, endian-specific indexing, final complement behavior, and seed compatibility with hardware implementations. The bulk loop casts byte pointers to `uint32_t *`; the code aligns to 4 bytes first, but portability still relies on target tolerance for this aliasing style in the WiredTiger build. Boundary coverage is important for zero-length input, 1-7 byte tails, and all possible pointer alignments.

## Test Signals
Relevant tests include `test/csuite/wt2695_checksum`, which compares hardware and software checksums, seeded cumulative checksums, misaligned buffers, varied lengths, and all-0xff data, plus `test/csuite/wt4117_checksum` and runtime block/log recovery tests that validate stored checksum compatibility.
