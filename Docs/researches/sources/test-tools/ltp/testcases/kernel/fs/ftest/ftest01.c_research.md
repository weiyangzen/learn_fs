# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest01.c

## Purpose

`ftest01.c` is a legacy sparse-file read/write verifier. Multiple child processes each operate on a separate file, randomly selecting fixed-size chunks, verifying unwritten chunks read as zero and previously written chunks retain a per-child byte pattern.

## Important APIs, Types, and Functions

Important functions are `setup`, `runtest`, `dotest`, `domisc`, `term`, and `cleanup`. State includes `iterations`, `nchild`, `csize`, `max_size`, child `fd`, `pidlist`, per-child `test_name`, bitmap arrays in `dotest`, and global misc-operation state `file_max`, `nchunks`, `last_trunc`, `tr_flag`, and `type`.

## Control Flow

`setup` creates an LTP temp directory and a private `ftest1.<pid>` subdirectory. `runtest` creates one file per child, forks children into `dotest`, waits for them, removes the subdirectory via `/bin/rm -rf`, and syncs. `dotest` repeatedly truncates the file, clears bitmaps, reads random chunks, verifies zero or current pattern, writes the pattern, and periodically calls `domisc`.

## State and Persistence Behavior

The file under test is sparse and per child. Bitmaps track which chunks should contain the current value after truncation. `domisc` injects `fsync`, alternating `truncate`/`ftruncate`, `sync`, and `fstat`, updating the bitmap after truncation.

## Dependencies and Integration Points

Uses legacy LTP `test.h`, `tso_safe_macros.h`, and `libftest` diagnostics. It depends on fork/wait, `lseek`, `read`, `write`, `truncate`, `ftruncate`, `fsync`, `sync`, `fstat`, and `/bin/rm`.

## Risks and Edge Cases

The test uses many globals shared after fork, exits from children through LTP functions, and can run for a long time. The bitmap model assumes sparse unwritten regions read as zeros and that truncation semantics are immediate. It shells out to `/bin/rm -rf` for cleanup.

## Test Signals

Pass requires all child exits to be zero and no data-compare, transfer-size, fstat-size, or syscall failures. On corruption it dumps buffer and bitmap state via `libftest`.
