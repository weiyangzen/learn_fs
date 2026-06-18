# File Research: sources/virtualization/libguestfs/daemon/sync.c

## Role
Implements daemon disk synchronization for guestfs `sync`, with Linux and Windows-specific flushing behavior.

## Main Flow
- `do_sync()` calls `sync_disks()` and reports failure.
- On Unix systems with `sync(2)`, `sync_disks()` calls `sync()` first.
- On Linux with `fsync`, `fsync_devices()` scans `/sys/block`, opens common disk-like devices, skips the appliance root device, and `fsync()`s each.
- On Windows, `sync_win32()` enumerates fixed logical drives and calls `FlushFileBuffers()` on volume handles.

## Semantics
The Linux path explicitly compensates for qemu writeback caching by fsyncing block devices after scheduling writes with `sync()`.

## Filesystem/Storage Relevance
This file is important for ensuring filesystem mutations performed inside the appliance reach the underlying virtual disks before the caller assumes persistence.
