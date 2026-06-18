# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate_freebsd.go`

## Purpose
FreeBSD fallocate implementation using `posix_fallocate` syscall.

## Important APIs, Types, And Functions
Calls `SYS_POSIX_FALLOCATE`, ignores mode, and converts nonzero return to `unix.Errno`.

## Control Flow
Calls `SYS_POSIX_FALLOCATE`, ignores mode, and converts nonzero return to `unix.Errno`.

## State And Persistence
State is allocated file blocks. Risk is lack of mode support and syscall return convention.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is allocated file blocks. Risk is lack of mode support and syscall return convention.

## Test Signals
State is allocated file blocks. Risk is lack of mode support and syscall return convention.
