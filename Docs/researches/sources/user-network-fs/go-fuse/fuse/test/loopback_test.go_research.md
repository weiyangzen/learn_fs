# `sources/user-network-fs/go-fuse/fuse/test/loopback_test.go`

## Purpose
Primary loopback integration suite and shared `testCase` harness.

## Important APIs, Types, And Functions
Defines mounting helpers plus tests for open/read/write/remove/link/forget/POSIX operations/access/mknod/readdir rename/fsync/large IO/statfs/symlink root/double open/chgrp/known-child attrs/utimens.

## Control Flow
Defines mounting helpers plus tests for open/read/write/remove/link/forget/POSIX operations/access/mknod/readdir rename/fsync/large IO/statfs/symlink root/double open/chgrp/known-child attrs/utimens.

## State And Persistence
State is temp backing directory, mountpoint, pathfs connector, kernel cache TTLs, and client inode mappings. It is the strongest signal for pathfs-loopback behavior. Risks are kernel timing, root permissions, and FUSE mount availability.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp backing directory, mountpoint, pathfs connector, kernel cache TTLs, and client inode mappings. It is the strongest signal for pathfs-loopback behavior. Risks are kernel timing, root permissions, and FUSE mount availability.

## Test Signals
State is temp backing directory, mountpoint, pathfs connector, kernel cache TTLs, and client inode mappings. It is the strongest signal for pathfs-loopback behavior. Risks are kernel timing, root permissions, and FUSE mount availability.
