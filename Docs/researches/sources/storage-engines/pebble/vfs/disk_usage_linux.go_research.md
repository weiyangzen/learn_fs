# Research: sources/storage-engines/pebble/vfs/disk_usage_linux.go

## Purpose
`vfs/disk_usage_linux.go` implements Linux disk-usage reporting for `defaultFS.GetDiskUsage`.

## Important APIs, Types, And Functions
The file defines `func (defaultFS) GetDiskUsage(path string) (DiskUsage, error)`. It calls `unix.Statfs`, then computes `AvailBytes`, `TotalBytes`, and `UsedBytes`.

## Control Flow
The function creates a `unix.Statfs_t`, invokes `unix.Statfs(path, &stat)`, returns an error on failure, and otherwise calculates byte counts. It uses `stat.Frsize` rather than `stat.Bsize` because Linux `Bavail` and `Bfree` are in fragment-size units and this matches `df`/coreutils behavior.

## State And Persistence
The function is read-only and has no persistent state. It returns a snapshot of filesystem usage at the time of the syscall.

## Dependencies And Integration Points
It depends on the Linux build tag and `golang.org/x/sys/unix`. It implements the `vfs.FS` disk usage hook used by wrappers and callers that report or enforce disk-space budgets.

## Risks And Edge Cases
Integer multiplication assumes the stat fields fit in `uint64`. `UsedBytes` uses `TotalBytes - freeBytes`, not `TotalBytes - availBytes`, so it includes blocks reserved for privileged users as used from an ordinary availability perspective. The `Frsize` choice is Linux-specific and intentionally differs from some other Unix files.

## Test Signals
Tests should compare against expected `df`-style values on Linux, verify error propagation for missing paths, and check that wrappers delegate `GetDiskUsage` to the inner FS.
