# sources/test-tools/ltp/testcases/kernel/fs/inode/inode01.c

## Purpose

`inode01.c` creates a bounded directory/file tree, records every generated path in `path_list`, then reopens the list to verify that directories still exist and files contain repeated copies of their path string.

## Important APIs, Types, and Functions

Important functions are `generate`, `check`, `get_next_name`, `increment_name`, `mode`, `escrivez`, `term`, `setup`, `blexit`, `blenter`, `fail_exit`, `anyfail`, and `ok_exit`. Constants define path length, eight-character names, max depth/breadth, file length, and modes.

## Control Flow

`main` constructs a unique root directory, creates `path_list`, writes the root directory record, recursively calls `generate`, then reopens `path_list` and calls `check`. `generate` alternates between file creation and directory creation by level, writes file contents, records names with trailing `F` or `D`, and recurses into directories. `check` reads each record, opens files and compares content repetitions, or stats directories and checks mode bits.

## State and Persistence Behavior

The generated tree persists under `inodeA<pid>` until removed with `rm -rf`. `path_list` is the durable manifest used for verification. Global buffers hold current name/path/read/write strings and fd state.

## Dependencies and Integration Points

Uses legacy LTP `test.h`, `mkdir`, `creat`, `open`, `write`, `read`, `stat`, signal handling, and `system("rm -rf ...")`.

## Risks and Edge Cases

Fixed-size path buffers limit tree size and rely on `snprintf` guards in newer patches. `open(path, READ)` treats fd 0 as failure because it checks `<= 0`. Cleanup uses shell `rm -rf`, and the signal handler performs non-async-safe I/O and cleanup.

## Test Signals

Pass requires both generation and checking blocks to report `TPASS` and final `TPASS`. Failures include manifest write/read errors, file content mismatches, missing directories, wrong mode bits, and cleanup cautions.
