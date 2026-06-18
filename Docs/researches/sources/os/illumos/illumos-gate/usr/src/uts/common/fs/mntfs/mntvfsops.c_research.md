# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvfsops.c

## Role

Implements module linkage and VFS operations for mntfs, the synthetic filesystem that exposes kernel mount-table information as `/etc/mnttab`.

## Major Responsibilities

- Registers the `mntfs` filesystem type and vnode operations.
- Creates the root synthetic vnode for a mntfs mount.
- Mounts mntfs only into the appropriate zone.
- Assigns unique synthetic device numbers for `stat(2)`.
- Handles unmount, root lookup, and statvfs for the synthetic one-file filesystem.

## Key Functions

- `_init()`: Installs the mntfs module.
- `_info()`: Returns module info.
- `mntinitrootnode()`: Initializes the root `mntnode_t` and its vnode. The vnode is marked root, no-cache, no-map, no-swap, and no-mount, and is a regular file.
- `mntinit()`: Registers VFS ops and vnode ops, stores `mntfstype`, allocates a unique major device number, and initializes the minor lock.
- `mntmount()`: Performs privilege and zone checks, sets resource to `"mnttab"`, allocates per-mount `mntdata_t`, checks mountpoint busy state, initializes zone reference, assigns unique minor, initializes root node, and attaches state to `vfsp`.
- `mntunmount()`: Requires unmount privilege, rejects unmount while root/open vnodes are active, releases zone reference, invalidates/frees the root vnode, and frees `mntdata_t`.
- `mntroot()`: Holds and returns the root synthetic vnode.
- `mntstatvfs()`: Returns synthetic statvfs data for `/mnttab`.

## Mount Semantics

`mntmount()` enforces:

- `secpolicy_fs_mount()`.
- In the global zone, the mountpoint path must resolve to the global zone itself; mntfs may not be mounted into another zone from outside.
- Non-overlay mounts require the mountpoint vnode to have no extra references and not already be a root.
- The VFS resource name is forced to `"mnttab"`.

The mounted filesystem consists of a single regular-file root vnode representing the mount table.

## Data and State

- `mntdata_t`: Per-mount data, including root node, zone reference, open count, cached size/mtime fields used by vnode ops.
- `mntnode_t`: Per-vnode state used by mntfs vnode operations.
- `mnt_major`, `mnt_minor`, `mnt_minor_lock`: Synthetic device number allocation.
- `mntfstype`: Filesystem type number assigned at registration.

## Edge Cases and Semantics

- There is no `_fini()` routine; comments state the module cannot be unloaded once loaded.
- `mntunmount()` checks both vnode count and `mnt_nopen`, because mntfs creates per-open vnodes in `mntvnops.c`.
- `mntstatvfs()` reports zero blocks, one file, no free files, `DEV_BSIZE`, arbitrary name max 64, and `/mnttab` strings.
- Root vnode is `VREG`, not `VDIR`, because `/etc/mnttab` behaves as a file.

## Dependencies

Pairs with `mntvnops.c` for actual file read/ioctl behavior. Uses zone refs, VFS registration, vnode allocation, synthetic device helpers, mount policy checks, and mntfs private data structures.
