# sources/storage-engines/wiredtiger/test/csuite/wt4117_checksum/main.c

## Purpose
WT-4117 smoke-tests the public WiredTiger CRC32C function selector API against fixed known vectors.

## Important APIs, Types, and Functions
- Calls `wiredtiger_crc32c_func()` to obtain `uint32_t (*)(const void *, size_t)`.
- `check` reports vector mismatches via `testutil_checkfmt`.
- Uses `dcalloc` for an aligned zeroed buffer.

## Control Flow
`main` calls `run`. `run` allocates a 100-byte buffer, retrieves the CRC function, verifies CRCs for 1 to 4 zero bytes, then verifies `"123456789"` and `"The quick brown fox jumps over the lazy dog"`. It frees the buffer and exits.

## State and Persistence Behavior
No WiredTiger connection or persistent state is created. All state is in-memory test vectors.

## Dependencies and Integration Points
The test depends on the external checksum selector exported by WiredTiger and the test utility allocation/assertion layer. It complements WT-2695 by testing the public function pointer API rather than internal hardware/software functions.

## Risks and Test Signals
Any vector mismatch indicates wrong dispatch or CRC implementation. Coverage is intentionally small and does not test seeded or random inputs.
