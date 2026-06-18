# File Research: sources/local-fs/btrfs-linux/fs/btrfs/props.h

This header declares the Btrfs property API implemented by `props.c`.

Public interface:
- `btrfs_props_init()` initializes the property handler table.
- `btrfs_set_prop()` sets or removes a property xattr and applies it to an inode.
- `btrfs_validate_prop()` validates property name and value.
- `btrfs_ignore_prop()` reports whether a valid property should be skipped for an inode.
- `btrfs_load_inode_props()` loads persisted inode properties using a supplied path.
- `btrfs_inode_inherit_props()` inherits parent directory properties into a child inode.

Role:
- Provides the property layer entry points to inode creation, xattr, and inode-load paths.
- Forward declares Btrfs transaction, inode, and path structures to avoid pulling full implementation headers into callers.
