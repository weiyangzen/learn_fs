# `sources/user-network-fs/go-fuse/fuse/test/mount_test.go`

## Purpose
Tests nested nodefs mounts under an existing FUSE mount.

## Important APIs, Types, And Functions
Covers mount-on-existing EBUSY, rename protection, readdir visibility, recursive mount access, unmount EBUSY with open files, default-node mounting, and fd liveness after GC.

## Control Flow
Covers mount-on-existing EBUSY, rename protection, readdir visibility, recursive mount access, unmount EBUSY with open files, default-node mounting, and fd liveness after GC.

## State And Persistence
State includes mounted child nodes and open file handles. Signals protect mount lifecycle, busy detection, tree integration, and finalizer-related fd stability.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes mounted child nodes and open file handles. Signals protect mount lifecycle, busy detection, tree integration, and finalizer-related fd stability.

## Test Signals
State includes mounted child nodes and open file handles. Signals protect mount lifecycle, busy detection, tree integration, and finalizer-related fd stability.
