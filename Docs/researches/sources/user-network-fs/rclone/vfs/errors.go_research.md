# sources/user-network-fs/rclone/vfs/errors.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors.go -->
## sources/user-network-fs/rclone/vfs/errors.go

Purpose: defines cross-platform low-level VFS error values and maps common errors to Go `os` package sentinels.

Important APIs and control flow: `Error` is a byte enum with values `OK`, `ENOTEMPTY`, `ESPIPE`, `EBADF`, `EROFS`, `ENOSYS`, and `ELOOP`. `ENOENT`, `EEXIST`, `EPERM`, `EINVAL`, and `ECLOSED` alias `os` errors. `Error.Error()` returns a human-readable string from `errorNames`, or `Low level error N` for unknown values.

State, dependencies, and integration: no mutable state. It depends on `fmt` and `os`. Comments note that mount/cmount/mount2 translation code must be updated when changing values.

Risks and test signals: enum ordering is part of external translation expectations, so adding/reordering errors has cross-package impact. Tests cover known and unknown string output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors.go -->
