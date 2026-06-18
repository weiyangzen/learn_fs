
# sources/user-network-fs/rclone/backend/local/local_internal_diskfull_test.go

## Purpose
Tests local backend ENOSPC detection and optional fatal wrapping.

## Important APIs, Types, And Control Flow
`TestIsDiskFullError` checks direct and wrapped `syscall.ENOSPC`, `file.ErrDiskFull`, `os.PathError`, and `os.SyscallError` cases. `updateWithReader` injects a reader that always returns a configured error into `Object.Update`. The remaining tests assert ENOSPC is non-fatal by default, fatal when `FatalIfNoSpace` is true, and unrelated errors are not made fatal.

## State And Persistence
Uses temporary fstest local directories and synthetic readers; no durable state.

## Dependencies And Integration Points
Depends on `fserrors`, `file.ErrDiskFull`, `object.NewStaticObjectInfo`, and local `Object.Update` defer logic.

## Risks And Test Signals
Strongly validates the backup-script safety feature. Remaining risk is platform-specific ENOSPC wrapping not represented by the cases; Plan 9 is excluded by build tag.
