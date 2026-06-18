# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vfsops.c

Read completely: 244 lines.

Purpose: implements devfs VFS mount, unmount, root, and statfs operations.

Key behavior:
- `devfs_mount()` rejects rootfs mounting, parses `from`, `export`, and `ruleset` options, rejects export, validates ruleset range, and enforces jail ruleset restrictions.
- Jail mounts always use the prison’s `pr_devfs_rsnum`.
- Mount updates can switch rulesets and reapply them.
- New mounts allocate `struct devfs_mount`, assign a mount index, initialize `dm_lock`, set local/shared-lookup/no-msync flags, create a root dirent with `DEVFS_ROOTINO`, instantiate/cache the root vnode, and optionally set a ruleset.
- `devfs_unmount()` flushes vnodes, performs cleanup, drops ruleset references, clears `mnt_data`, frees mount index, and finalizes if hold count reaches zero.
- `devfs_root()` allocates a vnode for `dm_rootdir` and marks it `VV_ROOT`.
- `devfs_statfs()` returns synthetic small filesystem statistics to satisfy callers such as `df`.

VFS registration:
- `devfs_vfsops` uses `vfs_cache_root` for normal root lookup and `devfs_root` as cachedroot callback.
- Registered as `VFCF_SYNTHETIC | VFCF_JAIL`.

Research notes:
- Devfs mount state has a hold count because vnode population may temporarily drop and reacquire mount locks while unmount can race.
