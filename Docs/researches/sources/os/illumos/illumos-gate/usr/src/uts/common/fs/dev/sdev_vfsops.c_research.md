# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vfsops.c

This file implements VFS/module operations for the illumos `/dev` filesystem.

Global state:
- `sdev_origins`, the mount info for the global `/dev` origin.
- `sdev_lock`, used for mount/unmount/rename synchronization.
- `sdev_taskq`, lazily created on first mount.
- `devmajor`, `devminor`, and linked-list `sdev_mntinfo` for mounted instances.
- `sdev_stale_attrvp`, a debug aid for stale attribute vnodes after remount.

Module and init flow:
- `_init()` initializes global lock, node cache, devfsadm locks, and installs the filesystem module.
- `_fini()` always returns `EBUSY`; the global `/dev` instance keeps the module loaded.
- `devinit()` registers VFS ops, creates default vnode ops, allocates a unique device major, initializes the plugin subsystem, and initializes the negative cache.

Mount flow:
- `sdev_mount()` checks mount privileges and mountpoint validity, copies mount arguments, resolves the attribute backing directory, lazily creates the taskq, and handles either remount or fresh mount.
- On remount, it stales existing nodes, replaces mount args and root attribute vnode, and updates mount time.
- On fresh mount, it allocates a unique dev_t, creates the root node with `sdev_mkroot()`, initializes `sdev_data`, inserts it into the mount list, and configures ACL flavor.
- For non-global instances, the root origin is set to the global `/dev` root.
- For the global instance, it sets up the negative cache and pre-fills dynamic root entries.

Unmount flow:
- `sdev_unmount()` enforces unmount/device privileges, rejects forced unmount, refuses to unmount the global instance, checks root vnode references, clears directory contents, destroys the root node, removes mount info from the linked list, and frees mount args/data.

Other VFS operations:
- `sdev_root()` returns the mounted root vnode with a hold.
- `sdev_statvfs()` returns synthetic filesystem stats suitable for a pseudo `/dev` filesystem.
- `sdev_find_mntinfo()` finds a mounted instance by root name and takes a root vnode hold.
- `sdev_mntinfo_rele()` releases that hold.
- `sdev_mnt_walk()` iterates all mounted instances under `sdev_lock`.

Important dependencies include module/VFS registration, `sdev_subr.c` node helpers, plugin initialization, negative-cache setup, profile update lookup by mount info, and backing attribute directory behavior.

Risk areas are remount stale-state handling, global versus non-global mount distinction, lifetime of root/origin holds, and linked-list consistency under `sdev_lock`.
