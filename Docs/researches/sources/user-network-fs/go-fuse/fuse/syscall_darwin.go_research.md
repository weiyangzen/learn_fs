# `sources/user-network-fs/go-fuse/fuse/syscall_darwin.go`

## Purpose
Darwin xattr syscall wrappers for the fuse package.

## Important APIs, Types, And Functions
Implements `getxattr`, `GetXAttr`, `listxattr`, `ListXAttr`, `Setxattr`, and `Removexattr` via direct syscalls and C strings.

## Control Flow
Implements `getxattr`, `GetXAttr`, `listxattr`, `ListXAttr`, `Setxattr`, and `Removexattr` via direct syscalls and C strings.

## State And Persistence
State is host xattr metadata. Risks include zero-length buffers/data, Darwin syscall argument order, and parsing NUL-separated names. Integrated by raw/path xattr operations.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is host xattr metadata. Risks include zero-length buffers/data, Darwin syscall argument order, and parsing NUL-separated names. Integrated by raw/path xattr operations.

## Test Signals
State is host xattr metadata. Risks include zero-length buffers/data, Darwin syscall argument order, and parsing NUL-separated names. Integrated by raw/path xattr operations.
