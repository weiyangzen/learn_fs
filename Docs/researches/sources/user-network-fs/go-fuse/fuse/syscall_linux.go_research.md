# `sources/user-network-fs/go-fuse/fuse/syscall_linux.go`

## Purpose
Linux `writev` wrapper.

## Important APIs, Types, And Functions
`writev` delegates to `unix.Writev` and returns byte count/error.

## Control Flow
`writev` delegates to `unix.Writev` and returns byte count/error.

## State And Persistence
No persistent state; it is the core response/notify write primitive on Linux. Risk is partial writes and errno propagation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state; it is the core response/notify write primitive on Linux. Risk is partial writes and errno propagation.

## Test Signals
No persistent state; it is the core response/notify write primitive on Linux. Risk is partial writes and errno propagation.
