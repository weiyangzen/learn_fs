# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vfsops.c

Read completely: 359 lines.

## Role

This file implements dirfs mount-level VFS operations and sysctl/debug registration. Dirfs mounts a host directory into a DragonFly vkernel, using host syscalls to validate and expose the host filesystem tree.

## Main Responsibilities

- Define dirfs allocation types and KTR tracepoints.
- Expose sysctls:
  - `vfs.dirfs.debug`
  - `vfs.dirfs.fd_limit`
  - `vfs.dirfs.fd_used`
  - `vfs.dirfs.passive_fd_list_miss`
  - `vfs.dirfs.passive_fd_list_hits`
- `dirfs_mount()`:
  - Handles read-only/read-write update toggles.
  - Allocates `struct dirfs_mount`.
  - Copies the host path from user or kernel space.
  - Strips trailing slash.
  - Verifies the host path exists and is a directory.
  - Initializes mount lock, vnode ops, fsid, vkernel uid/gid, passive fd list, inode tree, allocation limits, and mount stats.
- `dirfs_unmount()`:
  - Flushes vnodes.
  - Clears passive fd cache.
  - Closes/drops the root node if allocated.
  - Frees mount data.
- `dirfs_root()`:
  - Lazily allocates/stats the root node.
  - Opens and permanently keeps a host fd for the root directory.
  - Allocates the root vnode and marks it `VROOT`.
- `dirfs_statfs()` and `dirfs_statvfs()` mirror host filesystem stats into the mounted dirfs view.
- File-handle/export operations return unsupported.
- Registers `dirfs_vfsops` through `VFS_SET(dirfs_vfsops, dirfs, 0)`.

## Synchronization and Lifetime Model

- Mount state has `dm_lock` and `dm_token`, but mount setup largely happens during serialized VFS mount paths.
- Root node is held for the life of the mount by a node reference and an always-open host directory fd.
- Unmount expects `vflush()` to reclaim active vnodes before passive fd cache and root cleanup.

## Important Interactions

- Uses host functions: `stat()`, `open()`, `statfs()`, `statvfs()`, `getuid()`, and `getgid()`.
- Calls shared helpers from `dirfs_subr.c` for root stat, vnode allocation, closing, and node drop.
- Installs the vnode op table from `dirfs_vnops.c`.

## Research Notes

- `dirfs_mount()` has an error-path hazard: after `stat()` failure it jumps to `failure` without freeing `dmp`, unlike some earlier error branches.
- The read-only update path modifies only `dm_rdonly`; VOP paths also consult mount flags for write checks.
- NFS-style export/file-handle support is intentionally unsupported.
