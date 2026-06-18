# File Research: sources/os/linux/linux-stable/fs/btrfs/props.h

This header declares the Btrfs inode property API implemented in `props.c`.

Public API:
- `btrfs_props_init()` initializes the property handler hash table.
- `btrfs_set_prop()` sets or removes a known property through a transaction.
- `btrfs_validate_prop()` validates a property name/value pair for an inode.
- `btrfs_ignore_prop()` reports whether a validated property should be ignored for an inode.
- `btrfs_load_inode_props()` loads and applies properties from stored xattrs.
- `btrfs_inode_inherit_props()` inherits properties from a directory inode to a new inode.

Dependencies and declarations:
- Includes `<linux/types.h>` and `<linux/compiler_types.h>`.
- Forward declares Btrfs inode, path, and transaction handle types.

Role in the subsystem:
- Defines the narrow interface used by xattr, inode creation, and inode load paths to interact with Btrfs property handling.
