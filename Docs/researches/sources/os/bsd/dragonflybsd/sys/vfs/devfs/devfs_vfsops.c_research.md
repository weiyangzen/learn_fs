# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vfsops.c

Read completely: 284 lines.

## Role

This file implements DragonFlyBSD devfs mount-level VFS operations. It creates a per-mount devfs tree, attaches devfs vnode operation tables, exposes filesystem statistics, and tears down per-mount devfs state on unmount.

## Main Responsibilities

- `devfs_vfs_mount()`:
  - Rejects update mounts.
  - Copies optional `devfs_mount_info`.
  - Marks the mount local, synthetic-friendly, all-MPSAFE, no-stack-mount, and quick-halt.
  - Fills mount stat names and fsid.
  - Allocates `struct devfs_mnt_data`.
  - Determines jailed behavior from mount flags or credentials.
  - Creates the root `Nroot` devfs node.
  - Adds normal and special vnode op tables.
  - Registers the mount with devfs core, which populates existing devices.
- `devfs_vfs_unmount()`:
  - Flushes vnodes with optional forced close.
  - Cleans orphan nodes.
  - Removes the mount from the devfs core.
  - Frees mount data.
- `devfs_vfs_root()` returns the root vnode through `devfs_allocv()`.
- `devfs_vfs_statfs()` reports synthetic filesystem statistics and file counts.
- `devfs_vfs_fhtovp()`, `devfs_vfs_vptofh()`, and `devfs_vfs_vget()` translate between file handles/inodes and devfs vnodes.
- Namecache generation hooks store and test `mnt_namecache_gen` for devfs negative cache invalidation.
- Registers `devfs_vfsops` through `VFS_SET(devfs_vfsops, devfs, VFCF_SYNTHETIC | VFCF_MPSAFE)`.

## Synchronization and Lifetime Model

- Mount setup and root-node allocation occur under `devfs_lock`.
- Mount add/delete operations are sent synchronously to the devfs core thread.
- Unmount first calls `vflush()` so active vnodes are reclaimed before mount data is freed.
- The root node and all generated nodes are ultimately cleaned by `devfs_mount_del()`.

## Important Interactions

- Depends on `devfs_core.c` for node allocation, vnode allocation, mount registration, mount deletion, orphan counting, and inode-to-vnode lookup.
- Installs vnode op tables from `devfs_vnops.c`.
- Uses jail checks from `sys/jail.h`.

## Research Notes

- File handles use `boottime.tv_sec` as generation; stale boot-generation handles are rejected.
- `devfs_vfs_statfs()` reports two blocks to avoid divide-by-zero behavior in userland tools.
- Mount data is assigned before root node creation, so helpers can use `DEVFS_MNTDATA(mp)` during setup.
