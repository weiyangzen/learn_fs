# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/dv_node.h

This header defines devfs vnode-private `dv_node` structures and helper interfaces.

Node model:
- `dvnode_t` represents device filesystem nodes: directories for nexus drivers and character/block device nodes for devices.
- Fields include name/length, vnode, contents rwlock, underlying `dev_info_t`, parent pointer, AVL directory entries, AVL link, persistent attribute vnode, in-memory attributes, fake inode, flags, link count, busy count, device policy, default mode, and linked sdev node state.

Locking:
- `dv_contents` protects mutable directory/device fields below it and must be held for read before inspection and write before modification.

Flags and defaults:
- Node flags include out-of-date directory, ignore filesystem permissions, internal node, ACL present, and default mode set.
- Root inode is 2.
- Default uid/gid/modes are defined for directories and devices.
- Cleaning flags include force, reset permissions, and directory-lock-held.

Filesystem state:
- `devfs_data` stores root devfs node and VFS pointer.
- `dv_fid` overlays VFS fid for `VFS_VGET`.

Attribute macros:
- Compare and merge minor permissions (`mperm_t`) with vnode attributes.
- Shadow-node flags control creation and whether `dv_contents` is already write-held.

Traversal/helpers:
- AVL traversal macros expose first/next directory entry.
- Externs declare node cache init/fini, mkdir/root/create/destroy/insert/shadow/find/fill/clean/walk, devfs lookups, policy lookup, permission reset, remove-driver cleanup, and vnode ops.

Debugging:
- DEBUG builds expose `devfs_debug` flags and conditional printf-style macros.

Dependencies and relationships:
- Includes `sdev_impl.h`, tying legacy devfs and dynamic `/dev` support together.
- Uses device policy and devinfo holds to connect filesystem entries to device tree state.
