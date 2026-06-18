# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vfsops.c

This file implements VFS-level operations and module linkage for the illumos `/devices` filesystem (`devfs`). It initializes the filesystem type, creates the single devfs mount instance, exposes root/stat operations, and provides external cleanup and lookup helpers.

Core responsibilities:
- Defines module linkage for the `"devices filesystem"`.
- Registers devfs VFS operations and devfs vnode operations.
- Creates the fictitious devfs device number.
- Mounts devfs over the existing `/devices` vnode used as the attribute backing root.
- Keeps a global single mount instance in `devfs_mntinfo`.
- Exposes cleanup, lookup, walk, and device-policy helper APIs.

Important operations:
- `_init` initializes `devfs_lock`, creates the `dv_node` cache, and installs the filesystem module.
- `_fini` always returns `EBUSY`, reflecting that devfs is not unloaded in normal operation.
- `devfsinit` registers VFS ops, creates `dv_vnodeops`, and assigns `devfsdev`.
- `devfs_mount` enforces mount privilege and directory mountpoint type, creates the root `dv_node`, records the mountpoint as the root shadow attribute vnode, initializes `vfs_data`, fsid, block size, and timestamps.
- `devfs_unmount` always returns `EBUSY`.
- `devfs_root` returns a held root vnode.
- `devfs_statvfs` reports synthetic filesystem stats, using `kmem_cache_stat` for file count and zero block availability.
- `devfs_mountroot` rejects root mounting with `EINVAL`.
- `devfs_dip_to_dvnode` maps a `dev_info_t` to a cached devfs directory node using `ddi_pathname` and `devfs_lookupname`.
- `devfs_clean_vhci` cleans vHCI branches under `DV_CLEAN_FORCE`.
- `devfs_clean` performs best-effort cache cleanup for a devinfo subtree, sets `devfs_clean_key` to avoid configuration deadlocks, and optionally cleans vHCI branches relevant to DR.
- `devfs_lookupname` resolves a path relative to `/devices` with `kcred` and controlled root/directory arguments rather than using process credentials.
- `devfs_walk` resolves a `/devices`-relative path and walks cached `dv_node` entries via `dv_walk`.
- `devfs_devpolicy` extracts held device policy data from a devfs real vnode behind a specfs vnode.

Design notes:
- devfs is intended to be mounted by the kernel during boot, not by arbitrary userland.
- The mountpoint itself becomes the root attribute backing vnode.
- Cleanup is deliberately best effort and returns success even if some cached nodes remain busy, because device contracts or later releases may resolve references during offline processing.

Research notes:
- This file gives the public entry points used by device removal, driver unload cleanup, policy lookup, and path-based devfs introspection.
- The single-mount assumption is explicit through `ASSERT(devfs_mntinfo == NULL)` in `devfs_mount`.
