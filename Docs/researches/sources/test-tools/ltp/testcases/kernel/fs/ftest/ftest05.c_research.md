# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest05.c

## Purpose

`ftest05.c` is the large-file-offset variant of `ftest01`. It uses `lseek64` and `off64_t` in the same per-child sparse-file chunk verification pattern.

## Important APIs, Types, and Functions

Important functions mirror `ftest01`: `setup`, `runtest`, `dotest`, `domisc`, `term`, and `cleanup`. Key differences are `_LARGEFILE64_SOURCE`, `off64_t max_size`, `lseek64`, and the `CHUNK(i)` macro casting to `off64_t`.

## Control Flow

The parent creates a private directory, opens one file per child, forks children into `dotest`, waits, removes the work directory, and syncs. `dotest` repeatedly truncates, clears bitmaps, chooses random chunks, uses `lseek64` before reads and writes, verifies zero or pattern data, and injects misc operations.

## State and Persistence Behavior

Per-child sparse files are the persistent test objects until cleanup. Bitmap state models valid chunks and is adjusted after truncation. Diagnostic state records the last truncate offset and hold bitmap.

## Dependencies and Integration Points

Uses legacy LTP, `libftest`, fork/wait, `lseek64`, `read`, `write`, `truncate`, `ftruncate`, `fsync`, `sync`, `fstat`, and `/bin/rm`.

## Risks and Edge Cases

Although it uses 64-bit seek APIs, default `max_size` is still 1 MiB, so large-file coverage depends on modifying defaults or build/runtime environment. Some failure paths call `tst_exit` directly from children. Cleanup calls `tst_exit`, making the nominal `return 1` in `main` unreachable.

## Test Signals

Pass requires zero child exits and successful pattern checks. Failures report the 64-bit offset, transfer size, expected pattern, stat data, and bitmaps.
