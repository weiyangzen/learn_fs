# File Research: sources/os/linux/linux/fs/btrfs/props.h

This header declares the Btrfs property API implemented by `props.c`.

Public API:
- `btrfs_props_init()`
- `btrfs_set_prop()`
- `btrfs_validate_prop()`
- `btrfs_ignore_prop()`
- `btrfs_load_inode_props()`
- `btrfs_inode_inherit_props()`

Role:
- Provides entry points used by inode creation, inode load, and xattr/property paths.
- Uses forward declarations for Btrfs inode, path, and transaction structures to keep callers decoupled from implementation headers.
