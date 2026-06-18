# File Research: sources/os/linux/linux-stable/fs/configfs/configfs_internal.h

This header declares configfs internal structures, flags, shared locks, helpers, and operation tables.

Key responsibilities:
- Defines `struct configfs_fragment`, used to gate operations during directory teardown.
- Defines `struct configfs_dirent`, the internal tree node for directories, attributes, binary attributes, symlinks, and root.
- Defines dirent type/state flags such as `CONFIGFS_DIR`, `CONFIGFS_ITEM_ATTR`, `CONFIGFS_USET_DEFAULT`, `CONFIGFS_USET_DROPPING`, and `CONFIGFS_USET_CREATING`.
- Declares shared locks `configfs_symlink_mutex` and `configfs_dirent_lock`.
- Declares exported-internal functions for creating inodes, dirents, links, attributes, pinning the filesystem, dropping dentries, and setattr.
- Provides inline conversions from dentries to config items and attributes.
- Provides reference helpers `configfs_get()` and `configfs_put()` for dirents.

Dependencies:
- Used by every configfs implementation file.
- Depends on public configfs types from `<linux/configfs.h>`.

Risks and invariants:
- `CONFIGFS_PINNED` and `CONFIGFS_NOT_PINNED` classify children differently for lookup and lifetime.
- Dirent release frees persistent attributes and fragment references for non-root entries.
- `configfs_get_config_item()` only returns an item if the dentry is still hashed, preventing stale item access.
