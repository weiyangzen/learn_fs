# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate_linux.go`

## Purpose
Linux fallocate implementation.

## Important APIs, Types, And Functions
Delegates directly to `unix.Fallocate(fd, mode, off, len)`.

## Control Flow
Delegates directly to `unix.Fallocate(fd, mode, off, len)`.

## State And Persistence
State is host file allocation. Risk is kernel/filesystem support for mode flags; loopback Linux tests cover fallocate.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is host file allocation. Risk is kernel/filesystem support for mode flags; loopback Linux tests cover fallocate.

## Test Signals
State is host file allocation. Risk is kernel/filesystem support for mode flags; loopback Linux tests cover fallocate.
