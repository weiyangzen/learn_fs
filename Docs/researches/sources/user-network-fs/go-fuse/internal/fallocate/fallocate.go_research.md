# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate.go`

## Purpose
Cross-platform wrapper package for preallocating file space.

## Important APIs, Types, And Functions
Exports `Fallocate(fd, mode, off, len)` and delegates to platform `fallocate` implementation.

## Control Flow
Exports `Fallocate(fd, mode, off, len)` and delegates to platform `fallocate` implementation.

## State And Persistence
No state; host filesystem allocation persists. Integrated by loopback/nodefs allocation paths. Risk is mode support differing by OS.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state; host filesystem allocation persists. Integrated by loopback/nodefs allocation paths. Risk is mode support differing by OS.

## Test Signals
No state; host filesystem allocation persists. Integrated by loopback/nodefs allocation paths. Risk is mode support differing by OS.
