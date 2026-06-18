# `sources/user-network-fs/go-fuse/fuse/syscall_unix.go`

## Purpose
Non-Linux `writev` wrapper using raw `SYS_WRITEV`.

## Important APIs, Types, And Functions
Defines `sys_writev` and `writev`; builds syscall iovecs from non-empty packet slices and retries EINTR.

## Control Flow
Defines `sys_writev` and `writev`; builds syscall iovecs from non-empty packet slices and retries EINTR.

## State And Persistence
No persistence. Risks include empty packet slice handling, iovec lifetime, and platform syscall differences.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risks include empty packet slice handling, iovec lifetime, and platform syscall differences.

## Test Signals
No persistence. Risks include empty packet slice handling, iovec lifetime, and platform syscall differences.
