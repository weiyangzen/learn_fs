# `sources/user-network-fs/go-fuse/fuse/test/loopback_linux_test.go`

## Purpose
Linux-specific loopback tests for time, overlayfs, fallocate, and readdir inode details.

## Important APIs, Types, And Functions
Defines overlayfs flag setup plus tests `TestTouch`, `TestNegativeTime`, `TestUtimesNano`, `TestOverlayfs`, `TestFallocate`, `TestSpecialEntries`, and `TestReaddirInodes`.

## Control Flow
Defines overlayfs flag setup plus tests `TestTouch`, `TestNegativeTime`, `TestUtimesNano`, `TestOverlayfs`, `TestFallocate`, `TestSpecialEntries`, and `TestReaddirInodes`.

## State And Persistence
State uses temp loopback mounts and sometimes overlayfs. Signals validate nanosecond/negative timestamps, allocation, special directory entries, and inode reporting. Risks include kernel version and optional overlayfs flag.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State uses temp loopback mounts and sometimes overlayfs. Signals validate nanosecond/negative timestamps, allocation, special directory entries, and inode reporting. Risks include kernel version and optional overlayfs flag.

## Test Signals
State uses temp loopback mounts and sometimes overlayfs. Signals validate nanosecond/negative timestamps, allocation, special directory entries, and inode reporting. Risks include kernel version and optional overlayfs flag.
