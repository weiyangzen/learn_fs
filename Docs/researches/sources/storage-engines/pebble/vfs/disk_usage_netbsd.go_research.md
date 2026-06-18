# Research: sources/storage-engines/pebble/vfs/disk_usage_netbsd.go

## Purpose
`vfs/disk_usage_netbsd.go` implements NetBSD disk-usage reporting for `defaultFS.GetDiskUsage`.

## Important APIs, Types, And Functions
The file defines NetBSD's `GetDiskUsage` method using `unix.Statvfs_t` and `unix.Statvfs`.

## Control Flow
The method calls `unix.Statvfs(path, &stat)`, returns an empty `DiskUsage` plus error on failure, and otherwise multiplies `Bsize` by `Bfree`, `Bavail`, and `Blocks` to compute free, available, and total bytes. Used bytes are total minus free.

## State And Persistence
The method is read-only and returns a point-in-time filesystem usage snapshot.

## Dependencies And Integration Points
It is selected by the `netbsd` build tag and depends on `golang.org/x/sys/unix`. It implements the platform-specific branch of the VFS disk usage API.

## Risks And Edge Cases
The code assumes NetBSD `Bsize` is the correct unit for all block counts returned by `Statvfs`. Reserved blocks are counted as used because `UsedBytes` subtracts `Bfree`, while `AvailBytes` reports `Bavail`.

## Test Signals
Signals include successful `Statvfs` conversion, missing-path error propagation, and consistency with platform tools for total, used, and available bytes.
