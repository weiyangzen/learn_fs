# sources/sync-backup/bup/lib/bup/bupsplit.c

## Purpose
Implements rolling checksum support used by bup's content-defined splitter, plus an optional selftest.

## Important APIs, Types, and Functions
Exports `rollsum_sum(uint8_t *buf, size_t ofs, size_t len)` and, unless `BUP_NO_SELFTEST`, `bupsplit_selftest()`.

## Control Flow
`rollsum_sum` initializes a `Rollsum`, rolls bytes from offset to length, and returns the digest. The selftest fills a deterministic random buffer, compares rolling sums over shifted windows, prints sums, and returns nonzero on mismatch.

## State and Persistence Behavior
No persistence. State is stack/local rollsum and selftest heap buffer.

## Dependencies and Integration Points
Depends on `bupsplit.h` inline rollsum functions. Used by `_hashsplit.c` and `_helpers.c`.

## Risks and Test Signals
Risks are checksum regression altering split boundaries and selftest memory allocation failure not explicitly handled. Signals are selftest success and stable split behavior in higher-level tests.
