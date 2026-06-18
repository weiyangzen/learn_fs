# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vfsops.c

## Scope

Defines the LFS VFS module, sysctls, mount/unmount lifecycle, vnode loading/allocation, writer daemon, sync/stat operations, page-cache writeback integration, filesystem resize, and extended-attribute dispatch.

## APIs And Behavior

- `lfs_vfsops` registers LFS VFS entry points; module init/fini establishes legacy cleaner syscalls and attaches/detaches the filesystem.
- `lfs_sysctl_setup()` exposes LFS tuning, statistics, roll-forward, and debug controls.
- `lfs_writerd()` monitors global dirty-buffer/page pressure and per-filesystem pageout/dirop queues, triggering flushes or cleaner wakeups.
- `lfs_init()`, `lfs_reinit()`, and `lfs_done()` manage pools, global locks/CVs, ULFS initialization, and LFS workqueues.
- `lfs_mount()` handles new mounts, remounts, read-only/read-write transitions, device authorization/opening, and statvfs setup.
- `lfs_mountfs()` reads and validates primary/alternate superblocks, chooses the older checkpoint for recovery safety, builds `struct lfs`/`struct ulfsmount`, initializes queues/locks/reserve buffers, loads the Ifile, orders the inode freelist, frees orphans, rolls forward, marks the filesystem dirty for writable mounts, initializes cleaner info, marks the current segment active, and starts the writer daemon.
- `lfs_unmount()` and `lfs_flushfiles()` perform checkpoints, stop sleepers/cleaners, flush vnodes, write clean superblocks, drain I/O, close the device, and free per-mount state.
- `lfs_statvfs()`, `lfs_sync()`, `lfs_vget()`, `lfs_loadvnode()`, `lfs_newvnode()`, `lfs_fhtovp()`, and `lfs_vptofh()` implement VFS statistics, sync, vnode cache integration, disk inode loading, inode creation, and file handles.
- `lfs_gop_write()` is the LFS-specific genfs page write routine: it requires the segment lock, maps dirty pages, splits writes by holes/segment-summary capacity, gathers buffers into the active segment, and returns `EAGAIN` when the cleaner or caller must retry.
- `lfs_resize_fs()` rewrites or invalidates removed segments, shifts Ifile segment tables, adjusts superblock accounting, initializes new `SEGUSE` entries, truncates Ifile when shrinking, and updates cleaner info.
- `lfs_extattrctl()` routes ULFS1 extended-attribute control when configured, otherwise falls back to standard VFS behavior.

## State And Dependencies

This file owns top-level LFS mount state and integration with NetBSD VFS, UVM, genfs, ULFS, specfs, sysctl, syscall packages, and workqueues. Important state includes active superblock selection, segment usage trees, Ifile vnode, reserve memory, writer/cleaner queues, dirty-page counters, vnode pools, and roll-forward/mount flags.

## Risks And Invariants

Mount logic deliberately uses the older of two superblocks, then roll-forward completes before ordinary `vget` proceeds. Writable mounts immediately clear the clean flag in both superblocks to preserve crash semantics. Page writeback assumes the segment lock and active `fip` are prepared by callers. Resize has many coupled Ifile, segment table, and free-space accounting invariants; several error paths still panic or note incomplete cleanup.
