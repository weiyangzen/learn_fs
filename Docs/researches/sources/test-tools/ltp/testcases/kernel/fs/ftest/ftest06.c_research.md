# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest06.c

## Purpose

`ftest06.c` is the large-file-seek variant of `ftest02`, stressing inode and directory operations while using `lseek64` for sparse file creation.

## Important APIs, Types, and Functions

Core functions are `crfile`, `unlfile`, `fussdir`, `dotest`, `dowarn`, `term`, and `cleanup`. It uses `_LARGEFILE64_SOURCE`, `off64_t seekval`, `lseek64`, `ft_mkname`, and the same random `ino_thing` dispatch table as `ftest02`.

## Control Flow

For each LTP loop, `main` creates working and home directories, forks five children, each child repeatedly picks among file create/verify, unlink/rmdir, directory fussing, and sync. The parent waits, removes known generated names, removes both trees with `/bin/rm -rf`, syncs, reports, and cleans up.

## State and Persistence Behavior

Generated paths live under `dirname` and `homedir`. File creation writes a fixed message after a random up-to-1MiB 64-bit seek and verifies it immediately. Directory fussing temporarily changes cwd and may intentionally leave directories for cleanup.

## Dependencies and Integration Points

Uses legacy LTP `test.h`, `libftest`, fork/wait, directory syscalls, `lseek64`, optional mount cleanup branches, `sync`, and `/bin/rm`.

## Risks and Edge Cases

The optional mount cleanup variables are legacy and not initialized by normal flow. `dirlen` is set but unused. The large-file API is used with only 1MiB random seeks, so coverage is about API path more than very large offsets.

## Test Signals

Pass is all child exits zero and parent `TPASS`. `dowarn` emits child, errno, operation, and path on failure; incorrect non-empty-directory removal is a hard `TFAIL`.
