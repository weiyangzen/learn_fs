# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vnops.c

## Purpose

`sharefs_vnops.c` implements the vnode operations for the `sharefs` pseudo-file that presents the kernel share table as read-only text. It creates per-open snapshots so readers see stable sharetab contents while the underlying in-kernel share list may change.

## Main Interfaces

The vnode operation table `sharefs_tops_data[]` installs `sharefs_open`, `sharefs_close`, `sharefs_getattr`, `sharefs_access`, `sharefs_inactive`, `sharefs_read`, and `fs_seek`, with ioctl rejected by `fs_inval`.

Other important routines are `sharefs_snap_create()` and `sharefs_create_root_file()`.

## Behavior And Data Flow

`sharefs_create_root_file()` creates the mounted root pseudo-file with `gfs_root_create_file()` and marks it as the real sharetab vnode. `sharefs_open()` rejects write opens, creates a fresh GFS vnode for the open instance, holds the parent VFS, marks the vnode as uncached/unmappable/root-like pseudo data, releases the original vnode, and builds a snapshot.

`sharefs_snap_create()` locks `sharefs_lock` as writer and `sharetab_lock` as reader. If an existing snapshot matches `sharetab_generation`, it reuses it. Otherwise it frees stale snapshot memory, copies `sharetab_size` and `sharetab_count`, allocates a NUL-terminated buffer, walks each filesystem share table and hash bucket, formats entries as tab-separated `path res fstype opts descr` lines, records snapshot time and generation, and validates count/size accounting.

`sharefs_read()` refreshes the snapshot when reading from offset zero, bounds the requested read against `sharefs_size`, rejects negative offsets or impossible lengths, and copies from the snapshot with `uiomove()`.

`sharefs_getattr()` returns regular read-only file attributes. For the root/real vnode it reports current global sharetab size and mtime; for opened snapshot vnodes it reports snapshot size and time. `sharefs_close()` and `sharefs_inactive()` release snapshot buffers when the open instance is no longer used.

## Dependencies

The vnode code depends on sharetab globals and locks from `sharetab.c`, GFS file/root creation, `uiomove()`, vnode/VFS reference management, and `sharefs/sharefs.h` structures such as `shnode_t`, `sharetab_globals_t`, `sharetab_t`, and `share_t`.

## Research Notes

The central invariant is that text exported to userspace comes from a stable per-open snapshot, not from live sharetab entries while they can be replaced or removed. Audit points are size accounting in `sharefs_snap_create()`, generation reuse, lock ordering between `sharefs_lock` and `sharetab_lock`, and cleanup on open/read/inactive error paths.
