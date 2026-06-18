<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix.go -->
# sources/storage-engines/pebble/vfs/errors_unix.go

## Purpose
Defines Unix-specific filesystem error helpers for Pebble's VFS layer.

## Important APIs, Types, and Functions
`errNotEmpty` aliases `unix.ENOTEMPTY` for directory removal semantics. `IsNoSpaceError` returns true when an error wraps `unix.ENOSPC`.

## Control Flow
`IsNoSpaceError` delegates to `cockroachdb/errors.Is`, allowing wrapped errors from VFS calls to match the Unix errno.

## State and Persistence Behavior
No state or persistence. It only supplies platform constants and classification logic.

## Dependencies and Integration Points
Used by VFS and MemFS removal/error handling. Depends on `golang.org/x/sys/unix` and CockroachDB errors wrapping. Built only on Darwin, DragonFly, FreeBSD, Linux, OpenBSD, and NetBSD.

## Risks and Edge Cases
It only recognizes `ENOSPC`; other quota or inode exhaustion errors are not classified as no-space here. The build tag excludes Solaris despite Unix lock code including Solaris in a separate file.

## Test Signals
`errors_unix_test.go` verifies that a stack-wrapped `unix.ENOSPC` is recognized.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix.go -->
