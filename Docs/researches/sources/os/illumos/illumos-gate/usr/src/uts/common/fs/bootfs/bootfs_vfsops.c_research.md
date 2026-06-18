# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vfsops.c

## Purpose

`bootfs_vfsops.c` registers bootfs as a kernel filesystem and implements its VFS operations. Bootfs exposes boot-loader supplied modules as a read-only filesystem backed by memory already resident at boot.

## File Shape

- Size: 321 lines, 8,454 bytes.
- SHA-256: `8b93d8ae78b203908e2756481bd6cb57b62a45ff6c913898cdc8d81cef6da1f6`.
- Module entry points: `_init()`, `_info()`, `_fini()`.
- VFS operations: `bootfs_mount()`, `bootfs_unmount()`, `bootfs_root()`, `bootfs_statvfs()`.
- Init: `bootfs_init()`.

## Core Behavior

- `bootfs_mount()` checks mount privilege, requires a directory mountpoint, rejects remount, rejects busy non-overlay mountpoints, sets the resource name to `bootfs`, allocates `bootfs_t`, captures the mount path, allocates a minor number, creates a per-mount kstat, sets read-only/no-setuid/notrunc/unlinkable VFS flags, initializes node list and stats, and calls `bootfs_construct()`.
- `bootfs_unmount()` checks unmount privilege, rejects forced unmount, walks all bootfs nodes to ensure no vnode has more than the filesystem's own hold, deletes kstat, destructs nodes, frees mount path, minor ID, list, and `bootfs_t`.
- `bootfs_root()` returns a held root vnode for the mounted instance.
- `bootfs_statvfs()` reports page-sized block/fragments, no free blocks, file count from kstats, fsid, base type `bootfs`, and an empty filesystem string.
- `_init()` creates the node kmem cache, minor id space, module lock, and installs the filesystem module.
- `_fini()` refuses unload while active mounts exist, removes module linkage, frees vfs/vnode ops, destroys id space, mutex, and kmem cache.

## Dependencies And Contracts

- Shares global `bootfs_major`, `bootfs_node_cache`, and `bootfs_vnodeops` with the construct/vnode files.
- Uses `id_space_t` for minor allocation and kstat named counters for mounted instance statistics.
- Calls `bootfs_construct()`/`bootfs_destruct()` from `bootfs_construct.c`.

## Maintenance Notes

Bootfs is read-only and intentionally avoids swap-backed semantics: the module bytes are already memory-resident. The active mount counter `bootfs_nactive` is checked at unload time in this file; any changes to mount/unmount lifetime should keep that counter semantics correct.
