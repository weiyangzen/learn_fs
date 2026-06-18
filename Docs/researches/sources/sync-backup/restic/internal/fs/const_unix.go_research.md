# sources/sync-backup/restic/internal/fs/const_unix.go

Purpose: Provides Unix implementations of symlink/directory open flags.

Important APIs: `O_NOFOLLOW`, `O_DIRECTORY`, and `sanitizeFlags`.

Control flow and state: `sanitizeFlags` is identity on non-Windows systems because the package constants are valid OS flags.

Dependencies and integration: Consumed by `OpenFile`, `local.OpenFile`, `Readdirnames`, and tests that verify metadata-only symlink handling and FIFO directory reads.

Risks: Assumes `syscall.O_NOFOLLOW` and `syscall.O_DIRECTORY` are defined for non-Windows build targets selected by this file.

Test signals: `fs_local_test.go`, `fs_local_unix_test.go`, and `file_unix_test.go` exercise these flags through local filesystem operations.
