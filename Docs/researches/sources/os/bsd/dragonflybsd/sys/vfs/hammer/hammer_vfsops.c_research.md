# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vfsops.c

Purpose: registers HAMMER with the DragonFly VFS layer, exposes tunables/sysctls/statistics, and implements mount, unmount, root/vget, stat, sync, file-handle, and export operations.

Global controls: the file defines debug knobs, counters, dirty-buffer limits, record limits, REDO limits, fsync mode, noatime default, and SYSCTL entries under `vfs.hammer`. `hammer_vfs_init()` autosizes record and dirty-buffer limits and initializes reclaim limits.

Mount path: `hammer_vfs_mount()` handles both boot root mounts and normal mounts. It validates volume count and master id, allocates and initializes `hammer_mount`, lock refs, RB trees, tokens, volume lists, object-id/undo/reclaim lists, and root B-tree key bounds. It loads all volumes, checks root volume presence and volume completeness, installs vnode ops, caches the root blockmap, validates filesystem version, computes UNDO record limits, runs `hammer_recover_stage1()`, initializes fsid/stat fields, caches next TID and blockmap state, starts the flusher, obtains the root vnode, and runs `hammer_recover_stage2()` for read-write mounts.

Mount updates: read-only to read-write adjusts volume mode, flushes recovered buffers, runs stage2 recovery, refreshes blockmaps, and reloads inodes. Read-write to read-only reloads inodes, performs multiple flusher syncs, then adjusts volume mode.

Unmount/free: `hammer_vfs_unmount()` flushes vnodes and calls `hammer_free_hmp()`. The free path flushes dirty state, destroys inodes on critical error, asserts empty inode/flush structures, destroys the flusher, discards recovered buffers for read-only mounts, unloads buffers and volumes, destroys object-id caches and kmalloc pools, releases the filesystem token, and frees the mount.

VFS operations: `hammer_vfs_vget()` looks up an inode by object id and PFS localization and returns a locked vnode. `hammer_vfs_root()` vgets object id 1. `hammer_vfs_statfs()` and `hammer_vfs_statvfs()` report inode count and free blocks minus reserved space. `hammer_vfs_sync()` delegates to `hammer_sync_hmp()` unless panicking.

NFS/export support: `hammer_vfs_vptofh()` stores PFS id, object id, and as-of TID in file handles. `hammer_vfs_fhtovp()` reconstructs vnode lookups and can enforce root vnode PFS isolation for null-mounted PFS exports. `hammer_vfs_checkexp()` and `hammer_vfs_export()` integrate with DragonFly export controls.

Critical errors: `hammer_critical_error()` marks the mount critical, rate-limits a diagnostic, forces read-only mode by adjusting volume modes, records the error, and optionally enters the debugger.

Research notes: this file ties together nearly every other file in this group. The mount sequence is especially recovery-sensitive: stage1 runs before high-level B-tree use, while stage2 waits until the mount structure, flusher, and root vnode path are available.
