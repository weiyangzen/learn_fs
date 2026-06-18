# sources/sync-backup/bup/lib/bup/bupsplit.h

## Purpose
Header defining bup's rolling checksum state and inline operations for content-defined chunking.

## Important APIs, Types, and Functions
Defines `BUP_WINDOWBITS`, `BUP_WINDOWSIZE`, `ROLLSUM_CHAR_OFFSET`, `Rollsum`, `rollsum_init`, `rollsum_add`, `rollsum_roll`, `rollsum_digest`, `rollsum_sum`, and `bupsplit_selftest`.

## Control Flow
Inline functions initialize a rolling window, update checksum state by dropping/adding bytes, and combine `s1/s2` into a 32-bit digest. `rollsum_roll` is a macro for optimizer behavior.

## State and Persistence Behavior
No persistence. `Rollsum` stores rolling sums, a 64-byte window, and window offset.

## Dependencies and Integration Points
Used by `_hashsplit.c`, `_helpers.c`, and `bupsplit.c`.

## Risks and Test Signals
Risks are ABI/algorithm changes causing different chunk boundaries and dedup behavior. Signals are rollsum selftest and deterministic chunking tests.
