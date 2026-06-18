# sources/test-tools/ltp/testcases/kernel/fs/lftest/lftest.c

## Purpose

`lftest.c` verifies large-file write and seek behavior by writing a configurable number of 1 MiB buffers and seeking to the expected end position after each write.

## Important APIs, Types, and Functions

Functions are `setup` and `run`, wired through `struct tst_test`. Option `-n` controls `bufnum`, defaulting to 100 MiB. The static buffer `buf[TST_MB]` is filled with `A`, zeros, and `Z` sentinels.

## Control Flow

`setup` parses the buffer count and initializes the 1 MiB buffer. `run` creates `large_file`, writes the buffer `bufnum` times, calls `fsync` after each write, uses `lseek` to move to the next expected MiB boundary, closes the file, logs elapsed time, and reports pass.

## State and Persistence Behavior

The persistent test object is `large_file` in an LTP temporary directory. The file size is `bufnum` MiB if all writes and seeks succeed.

## Dependencies and Integration Points

Uses modern LTP `tst_test.h`, large-file compile flags from the Makefile, `creat`, `write`, `fsync`, `lseek`, and `time`.

## Risks and Edge Cases

It does not read back data, so it primarily tests syscall success and file growth rather than content integrity. `fsync` after every MiB can make the test slow. Disk-space exhaustion is reported as `TFAIL`.

## Test Signals

Pass is `TPASS "test successful"` after all writes/seeks. `TBROK` indicates invalid options or `creat` failure; `TFAIL` indicates write or seek failure.
