# sources/sync-backup/restic/internal/fs/const.go

Purpose: Re-exports a portable subset of OS open flags through the `fs` package.

Important APIs: Constants `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_APPEND`, `O_CREATE`, `O_EXCL`, `O_SYNC`, `O_TRUNC`, and `O_NONBLOCK`.

Control flow and state: No runtime behavior. Values are copied from `syscall` so callers can depend on `internal/fs` rather than importing platform syscalls directly.

Dependencies and integration: Used by `FS.OpenFile`, local wrappers, reader filesystem tests, and directory read helpers. Platform-specific `const_unix.go` and `const_windows.go` add `O_NOFOLLOW`, `O_DIRECTORY`, and `sanitizeFlags`.

Risks: Constants mirror Go/syscall values; portability depends on build targets exposing equivalent constants.

Test signals: Indirectly tested by local/reader filesystem tests that pass these flags into `OpenFile`.
