# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest08.c

## Purpose

`ftest08.c` is the large-file-offset variant of `ftest04`, stressing concurrent `readv`/`writev` access to one shared file with child-specific interleaved chunks and `lseek64`.

## Important APIs, Types, and Functions

Key functions are `init`, `runtest`, `dotest`, `domisc`, `term`, and `cleanup`. Important state includes `filename`, `iterations`, `nchild`, `csize`, `max_size`, `misc_flag`, per-child `bits`, iovec arrays, and the 64-bit `CHUNK(i)` macro.

## Control Flow

Each LTP loop initializes a temp file, forks children, and each child opens the shared file. In `dotest`, the child reads its assigned offset range with `readv`, verifies zero or previous value, writes current value with `writev`, fills any missed chunks, and alternates `fsync` and `sync` through `domisc`.

## State and Persistence Behavior

The single shared file is removed after each run. Children avoid overlapping writes by computing offsets from tester count and child ID. `val0` tracks the previous iteration's expected byte pattern.

## Dependencies and Integration Points

Uses legacy LTP, vector I/O, `lseek64`, fork/wait, `fsync`, `sync`, `fstat`, and `libftest` diagnostics.

## Risks and Edge Cases

Correctness depends on disjoint chunk math rather than locks. `tst_tmpdir()` is called in `init` for each loop, while cleanup is deferred to the end. Some format strings are legacy and noisy, and default sizes do not force genuinely large offsets.

## Test Signals

Pass is zero child exit status and no compare failure. A failure includes child number, 64-bit offset, expected value, stat data, iovec dump, and bitmap dump.
