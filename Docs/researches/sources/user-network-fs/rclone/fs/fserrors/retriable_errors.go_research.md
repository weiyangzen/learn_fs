<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors.go -->
# sources/user-network-fs/rclone/fs/fserrors/retriable_errors.go

## Purpose
Adds common non-Plan9 syscall errors to the package-level retriable error list.

## Important APIs, Types, And Control Flow
An `init` function appends `EPIPE`, `ETIMEDOUT`, `ECONNREFUSED`, `EHOSTDOWN`, `EHOSTUNREACH`, `ECONNABORTED`, `EAGAIN`, `EWOULDBLOCK`, and `ECONNRESET` to `retriableErrors`.

## State And Persistence
Mutates the package global retriable error slice at initialization.

## Dependencies And Integration Points
Selected by `!plan9` build tag and feeds `ShouldRetry`.

## Risks And Test Signals
Classification is platform and errno identity dependent. Tests for syscall causes provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors.go -->
