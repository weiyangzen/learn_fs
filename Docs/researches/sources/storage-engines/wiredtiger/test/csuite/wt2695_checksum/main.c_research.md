# sources/storage-engines/wiredtiger/test/csuite/wt2695_checksum/main.c

## Purpose
WT-2695 is a C-suite checksum smoke and stress test for WiredTiger's internal CRC32C implementations. It validates known CRC32C vectors, hardware and software parity, seeded cumulative CRC behavior, random payloads, and unaligned buffers.

## Important APIs, Types, and Functions
- Uses `test_util.h` harness types, especially `TEST_OPTS`, `WT_RAND_STATE`, `testutil_parse_opts`, `testutil_recreate_dir`, `testutil_cleanup`, `testutil_assertfmt`, and allocation helpers.
- Calls `wiredtiger_open` only to initialize a standard test home and statistics logging.
- Exercises internal checksum APIs: `__wt_checksum`, `__wt_checksum_sw`, `__wt_checksum_with_seed_sw`, and external selector `wiredtiger_crc32c_with_seed_func`.
- `check` centralizes equality assertions with byte length and diagnostic text.
- `cumulative_checksum` applies a seeded checksum function across fixed-size chunks and verifies equivalence with one-shot CRC.

## Control Flow
`main` parses options, recreates the home directory, opens WiredTiger, initializes random state, and allocates a 128 KiB data buffer plus a 32-byte `0xff` buffer. It then runs fixed vectors for zero bytes, all-`0xff` bytes, `"123456789"`, and `"The quick brown fox jumps over the lazy dog"`, including chunked cumulative calculations where length permits. It follows with 1000 power-of-two random buffers, 1000 random-length random buffers, and a 16x16 matrix of short lengths and misalignments.

## State and Persistence Behavior
The test creates a WiredTiger home with statistics logging but does not create tables or persistent user data. The relevant state is in memory: deterministic expected checksum constants, random payload bytes, and cumulative seed values. The unaligned checks deliberately pass shifted pointers into stack data.

## Dependencies and Integration Points
This test depends on WiredTiger internal checksum symbols and the CRC32C dispatch function. It integrates with the csuite runner through the standard `TEST_OPTS` home handling. s390x has guarded skips for seeded software CRC checks due to `FIXME-WT-12067`.

## Risks and Test Signals
Failures indicate CRC vector mismatch, hardware/software divergence, bad seeded CRC composition, or unaligned-read bugs. Random coverage is broad but not deterministic unless the underlying harness seed is fixed. The test is platform-sensitive on s390x because seeded software CRC assertions are disabled there.
