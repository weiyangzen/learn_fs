# `sources/user-network-fs/go-fuse/fuse/pathfs/syscall_linux.go`

## Purpose
Provides Linux syscall helpers for pathfs xattr listing/getting and `utimensat` with no-follow semantics.

## Important APIs, Types, And Functions
Key helpers are `getXAttr`, `listXAttr`, `_AT_SYMLINK_NOFOLLOW`, and `sysUtimensat`.

## Control Flow
Key helpers are `getXAttr`, `listXAttr`, `_AT_SYMLINK_NOFOLLOW`, and `sysUtimensat`.

## State And Persistence
The helpers allocate buffers after probing sizes and parse NUL-separated xattr names. Risks include empty xattr list handling, direct syscall ABI drift, and `dest[0]` assumptions for non-empty buffers. `syscall_test.go` validates `sysUtimensat`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
The helpers allocate buffers after probing sizes and parse NUL-separated xattr names. Risks include empty xattr list handling, direct syscall ABI drift, and `dest[0]` assumptions for non-empty buffers. `syscall_test.go` validates `sysUtimensat`.

## Test Signals
The helpers allocate buffers after probing sizes and parse NUL-separated xattr names. Risks include empty xattr list handling, direct syscall ABI drift, and `dest[0]` assumptions for non-empty buffers. `syscall_test.go` validates `sysUtimensat`.
