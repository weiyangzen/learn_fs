# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vfsops.c

## Role

This file implements the wrapper functions for mount-level VFS operations stored in `mp->mnt_op` or `vfc->vfc_vfsops`. Its main job is to centralize MPSAFE handling around filesystem VFS callbacks.

## Main Responsibilities

- Wraps mount operations:
  - `vfs_mount()`
  - `vfs_start()`
  - `vfs_unmount()`
  - `vfs_root()`
  - `vfs_quotactl()`
  - `vfs_statfs()`
  - `vfs_statvfs()`
  - `vfs_sync()`
  - `vfs_vget()`
  - `vfs_fhtovp()`
  - `vfs_checkexp()`
  - `vfs_vptofh()`
  - `vfs_extattrctl()`
- Wraps filesystem type lifecycle operations:
  - `vfs_init()`
  - `vfs_uninit()`
- Handles mount credentials during mount:
  - `vfs_mount()` stores a held credential in `mp->mnt_cred` if not already present, preserving jail/prison association.
- Handles accounting lifecycle:
  - `vfs_start()` calls `VFS_ACINIT()` for non-update mounts after successful start.
  - `vfs_unmount()` calls `VFS_ACDONE()` before invoking filesystem unmount.
- Stops the per-mount syncer thread after a successful filesystem unmount.

## Synchronization and MPSAFE Model

- Most wrappers use `VFS_MPLOCK_DECLARE`, `VFS_MPLOCK()`, `VFS_MPLOCK_FLAG()`, and `VFS_MPUNLOCK()` around the underlying filesystem callback.
- `vfs_start()` uses `VFS_MPLOCK_FLAG(mp, MNTK_ST_MPSAFE)`, allowing a distinct MPSAFE flag for start operations.
- `vfs_init()` and `vfs_uninit()` call filesystem type operations directly rather than locking a mount.

## Notable Design Details

- `vfs_start()` translates `EMOUNTEXIT` to success after the callback, matching DragonFly's mount-start control semantics.
- `vfs_unmount()` captures `mp->mnt_kern_flag` into a local `flags` variable but does not use it; this appears to be vestigial or preserved for debug/build history.
- `vfs_vptofh()` locks based on `vp->v_mount`, since the operation is vnode-derived rather than passed a mount explicitly.

## Cross-File Relationships

- These wrappers are the concrete functions behind many `VFS_*` macro calls used by `vfs_syscalls.c`, `vfs_subr.c`, and `vfs_synth.c`.
- `vfs_unmount()` interacts with the syncer infrastructure from `vfs_sync.c` by calling `vn_syncer_thr_stop()` after successful unmount.
- `vfs_mount()` stores mount credentials later used by jail and unmount visibility checks in `vfs_syscalls.c`.

## Research Notes

- This is a small but important abstraction layer. It ensures filesystem implementations do not each duplicate MP-lock wrapping and mount accounting hooks.
- Changes here affect every filesystem VFS operation dispatch path.
