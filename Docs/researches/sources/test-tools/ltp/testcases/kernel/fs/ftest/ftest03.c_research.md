# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest03.c

## Purpose

`ftest03.c` is the vector-I/O variant of `ftest01`. It verifies sparse-file chunk behavior using `readv` and `writev` across 16 iovec segments per chunk.

## Important APIs, Types, and Functions

Key functions are `setup`, `runtest`, `dotest`, `domisc`, and `term`. Important constants are `MAXIOVCNT`, `K_2` default chunk size, and bitmap/misc globals. `dotest` maintains read iovecs, value iovecs, zero iovecs, and `bits`/`hold_bits`.

## Control Flow

The parent creates a private directory, creates one file per child, forks children, waits, removes the directory, and syncs. Each child allocates 16 iovec buffers, resets file and bitmaps per iteration, reads random chunks with `readv`, verifies zero or pattern segments, writes the pattern with `writev`, and periodically runs `domisc`.

## State and Persistence Behavior

Each child owns a separate sparse file. The bitmap records chunks expected to contain the current pattern; truncation clears bitmap regions beyond the new file size. `hold_bits` preserves diagnostic history for failure output.

## Dependencies and Integration Points

Uses `test.h`, `tso_safe_macros.h`, `libftest`, `readv`, `writev`, `lseek`, `truncate`, `ftruncate`, `fsync`, `fstat`, `sync`, fork/wait, and `/bin/rm`.

## Risks and Edge Cases

`csize` must be divisible by `MAXIOVCNT`; the default is, but there is no active option parser enforcing alternate values. The file has legacy one-loop exit behavior after `tst_rmdir`. Allocation intentionally scatters buffers, increasing memory pressure and making failures harder to reproduce.

## Test Signals

Pass requires all child exits to be zero. Data mismatches dump the failing iovec and bitmap state; transfer-size, lseek, truncate, fsync, or fstat failures cause `TFAIL`/`TBROK`.
