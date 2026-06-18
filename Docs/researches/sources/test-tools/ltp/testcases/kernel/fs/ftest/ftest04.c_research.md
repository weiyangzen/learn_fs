# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest04.c

## Purpose

`ftest04.c` stresses concurrent vector I/O to a single shared file. Each child owns an interleaved set of chunks and verifies that its assigned chunks transition from zero to its own byte pattern.

## Important APIs, Types, and Functions

Key functions are `setup`, `runtest`, `dotest`, `domisc`, and `term`. `CHUNK(i)` maps a child and chunk index into non-overlapping offsets `((i * testers + me) * csize)`. State includes `filename`, `iterations`, `nchild`, `csize`, `max_size`, `misc_intvl`, per-child bitmaps, and iovec arrays.

## Control Flow

`setup` creates one shared file. `runtest` forks children; each child opens the same file and runs `dotest`. `dotest` reads assigned random chunks with `readv`, verifies zero or the previous iteration value, writes the current value with `writev`, fills any missed chunks at iteration end, and periodically calls `domisc`.

## State and Persistence Behavior

The shared file persists for the test run and is unlinked after children finish. Per-child bitmaps are private and valid because the offset formula partitions the file. `val0` tracks the previous iteration's pattern; `val` is the current pattern.

## Dependencies and Integration Points

Uses legacy LTP APIs, `readv`/`writev`, fork/wait, `fsync`, `sync`, `fstat`, `lseek`, and `libftest` diagnostics.

## Risks and Edge Cases

There is no locking; correctness depends entirely on disjoint chunk assignment. The test fills missing chunks at iteration end, so early loop termination may mask some timing patterns. It exits after one LTP loop.

## Test Signals

Passing requires zero child exit statuses and the parent reporting `TPASS`. Mismatches include child number, offset, expected value, stat info, iovec dump, and bitmap dump.
