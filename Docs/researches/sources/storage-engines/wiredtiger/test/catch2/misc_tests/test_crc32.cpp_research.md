# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_crc32.cpp

## Purpose
Tests WiredTiger CRC32C function pointers for empty input, seeded empty input, known vectors, long data, and incremental seeded computation.

## Important APIs, Types, And Functions
Uses `wiredtiger_crc32c_func()` and `wiredtiger_crc32c_with_seed_func()` to obtain function pointers. Builds vectors and strings for known checksums.

## Control Flow
The test asserts empty buffers produce zero or preserve the seed, checks known byte patterns, constructs a repeated long string, verifies its checksum, then recomputes the same checksum incrementally by feeding chunks with the previous CRC as seed.

## State And Persistence Behavior
No persistence. Random seed is used only for checking seeded zero-length input returns the seed.

## Dependencies And Integration Points
Depends on Catch2, `<ctime>`, `<cmath>`, vectors/strings, and `wt_internal.h`. It validates the selected platform CRC implementation through the public function pointer accessor.

## Risks And Edge Cases
Covers null pointers with zero length, seed preservation, all-zero/all-one bit patterns, and chunked computation equivalence.

## Test Signals
Exact checksum constants must match, including final incremental checksum `0x47a00ee5`.
