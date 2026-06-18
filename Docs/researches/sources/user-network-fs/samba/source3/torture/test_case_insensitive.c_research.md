# sources/user-network-fs/samba/source3/torture/test_case_insensitive.c

## Purpose
`test_case_insensitive.c` is a regression test for Samba bug 8042 involving file creation below a directory whose case differs from a prior path check on case-insensitive filesystems.

## Important APIs, types, and functions
The exported function is `run_case_insensitive_create`. It uses `cli_mkdir`, `cli_chkpath`, `cli_openx`, `cli_close`, `cli_unlink`, and `cli_rmdir`.

## Control flow
The test opens an SMB connection, creates directory `x`, verifies `X` exists with `cli_chkpath`, then creates `x\y`. If `cli_openx` returns `NT_STATUS_FILE_IS_A_DIRECTORY`, it prints a specific bug-reappeared message. Cleanup unlinks `x\y` and removes `x`.

## State and persistence behavior
The only persistent artifacts are temporary `x` and `x\y`, both removed on the normal cleanup path. Errors can leave them behind.

## Dependencies and integration points
It is part of the `smbtorture3` POSIX/local regression set via `proto.h`. It depends on server-side case-insensitive pathname handling and client open/checkpath helpers.

## Risks and test signals
The key signal is that `x\y` must be created as a file even after checking `X`. Failures indicate case-folding or name-cache confusion, especially on case-insensitive backing filesystems such as macOS.
