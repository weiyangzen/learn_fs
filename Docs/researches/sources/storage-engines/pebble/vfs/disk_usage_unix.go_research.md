# Research: sources/storage-engines/pebble/vfs/disk_usage_unix.go

## Purpose
`vfs/disk_usage_unix.go` implements default VFS disk-usage reporting for Darwin, DragonFly, and FreeBSD.

## Important APIs, Types, And Functions
The file defines `GetDiskUsage` using `unix.Statfs_t`, `unix.Statfs`, and fields `Bsize`, `Bfree`, `Bavail`, and `Blocks`.

## Control Flow
The method performs `Statfs`, propagates errors, computes free bytes from all free blocks, available bytes from user-available blocks, total bytes from all blocks, and used bytes as total minus free.

## State And Persistence
The method is read-only. It captures filesystem usage at the moment of the stat call.

## Dependencies And Integration Points
It is selected by build tags for Darwin, DragonFly, and FreeBSD and depends on `golang.org/x/sys/unix`. It backs `vfs.FS.GetDiskUsage` for disk-space reporting and wrappers on those platforms.

## Risks And Edge Cases
The implementation assumes `Bsize` is the correct multiplier for block counts across these platforms. It does not account for path-level quotas or container limits beyond what `Statfs` exposes. Reserved space is not available but is not included in `UsedBytes` beyond the total-minus-free calculation.

## Test Signals
Signals include correct conversion on supported Unix platforms, error propagation for bad paths, and wrapper delegation through disk-health and disk-full FS layers.
