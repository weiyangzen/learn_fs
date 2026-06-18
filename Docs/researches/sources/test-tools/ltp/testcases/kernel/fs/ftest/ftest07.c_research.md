# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest07.c

## Purpose

`ftest07.c` is the large-file-offset vector-I/O variant of `ftest03`. It verifies sparse per-child files with `lseek64`, `readv`, and `writev`.

## Important APIs, Types, and Functions

Important functions are `setup`, `runtest`, `dotest`, `domisc`, and `term`. It uses `_LARGEFILE64_SOURCE`, `off64_t max_size`, an inline `CHUNK(off64_t)`, 16 read/value/zero iovecs, and bitmap diagnostics from `libftest`.

## Control Flow

The parent creates a private test directory, opens one file per child, forks children, waits, removes the directory, and syncs. Each child allocates iovec buffers, truncates its file per iteration, reads random chunks with `readv` after `lseek64`, validates zero or current pattern, writes with `writev`, and periodically injects `fsync`, `truncate`/`ftruncate`, `sync`, and `fstat`.

## State and Persistence Behavior

Each child has its own sparse file and private model bitmaps. `file_max` is a 64-bit unsigned value updated after writes and truncations. `last_trunc` and `hold_bits` support diagnostics.

## Dependencies and Integration Points

Uses legacy LTP `test.h`, `tso_safe_macros.h`, `libftest`, vector I/O, large-file seek, truncate APIs, fork/wait, and `/bin/rm`.

## Risks and Edge Cases

The default size remains small despite 64-bit offsets. `last_trunc` is an `int`, so diagnostic precision is weaker than the 64-bit `file_max`. Like other ftest vector variants, `csize` must divide evenly by `MAXIOVCNT`.

## Test Signals

Pass means all children exit zero and no compare/syscall failures occur. Failures dump the precise 64-bit offset, stat state, failed iovec, and bitmap information.
