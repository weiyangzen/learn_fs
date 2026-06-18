# sources/object-store/minio/cmd/xl-storage_noatime_supported.go

## Purpose
This Linux/Unix build file defines optimized open flags for MinIO storage on Unix platforms that support no-atime reads and data-synchronous writes.

## Important APIs, Types, and Functions
It defines `readMode = os.O_RDONLY | 0x40000 | syscall.O_NONBLOCK`, where `0x40000` is `O_NOATIME`, and `writeMode = 0x1000 | syscall.O_NONBLOCK`, where `0x1000` is `O_DSYNC`.

## Control Flow
There is no runtime branching. Build tags select this file for `unix && !darwin && !freebsd`, and `xlStorage` inherits the flags for all ordinary read opens and sync metadata writes.

## State and Persistence Behavior
`O_NOATIME` avoids read-side access-time updates, reducing metadata churn on storage disks. `O_DSYNC` makes synchronous writes persist file data needed for consistency without necessarily syncing unrelated metadata. `O_NONBLOCK` avoids syscall behavior around epoll setup on files.

## Dependencies and Integration Points
The file depends on `os` and `syscall`. Its values are used by the central storage implementation in `xl-storage.go`, so any platform mismatch affects every local disk operation.

## Risks and Test Signals
The numeric constants are Linux-specific and can be fragile if used on an unsupported target, but build tags constrain that. Test coverage is mostly behavioral through storage read/write tests and Unix umask tests, not direct assertions of no-atime behavior.
