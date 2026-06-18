# File Research: sources/os/linux/linux/fs/btrfs/xattr.c

## Purpose
Implements Btrfs extended-attribute get, set, remove, list, VFS xattr handlers, Btrfs property xattr handling, and security-xattr initialization during inode creation.

Btrfs stores xattrs as `BTRFS_XATTR_ITEM_KEY` dir-item-style records under the inode objectid. A leaf item can contain one or more packed `struct btrfs_dir_item` entries.

## Main Operations
- `btrfs_getxattr()` looks up a named xattr, returns its length for zero-size probes, validates caller buffer size, and copies the value from the leaf after the packed name.
- `btrfs_setxattr()` inserts, replaces, or deletes one xattr inside an existing transaction.
- `btrfs_setxattr_trans()` starts or reuses a transaction, calls `btrfs_setxattr()`, updates inode ctime/version, and persists the inode item.
- `btrfs_listxattr()` scans all xattr items for an inode and returns NUL-terminated names or total required size.

## Set/Replace/Delete Semantics
`btrfs_setxattr()` enforces `BTRFS_MAX_XATTR_SIZE(root->fs_info)` for name plus value. A `NULL` value means removal; an empty non-NULL value means an empty xattr.

For `XATTR_REPLACE`, the code does a read-only lookup first so missing xattrs return `-ENODATA`. The comment relies on the VFS inode lock to prevent racing with concurrent xattr deletion.

Insertion uses `btrfs_insert_xattr_item()`. Existing packed items are handled through `-EOVERFLOW` or `-EEXIST`, then `btrfs_match_dir_item_name()` identifies the matching dir item.

Replacement is explicitly atomic from reader perspective:
- If this is the only xattr in the leaf item, the item is extended or truncated in place.
- If multiple xattrs share the item, the old name is deleted and the item is extended for the new entry.
- The value length and value bytes are then updated in the leaf.

Successful mutation marks `BTRFS_INODE_COPY_EVERYTHING` and clears `BTRFS_INODE_NO_XATTRS`.

## VFS Handler Integration
The file defines handlers for:
- `security.*`
- `trusted.*`
- `user.*`
- `btrfs.*` properties

`btrfs_xattr_handlers[]` exports these handlers to the inode operations layer.

Generic handler get/set paths prepend the full xattr prefix with `xattr_full_name()`. Set paths reject read-only roots with `-EROFS`.

Security handlers special-case `security.capability`:
- Missing capability xattr is cached with `BTRFS_INODE_NO_CAP_XATTR`.
- Setting capability clears that cached negative bit.

## Btrfs Property Handling
`btrfs_xattr_handler_set_prop()` validates a `btrfs.*` property through `btrfs_validate_prop()`, ignores properties rejected by `btrfs_ignore_prop()`, starts a transaction, applies `btrfs_set_prop()`, updates inode version/ctime, and persists the inode.

## Security Initialization
`btrfs_xattr_security_init()` calls `security_inode_init_security()` with `btrfs_initxattrs()`.

`btrfs_initxattrs()`:
- Runs under an existing transaction handle passed as `fs_private`.
- Enters a NOFS allocation context to avoid reclaim recursion while holding a transaction.
- Builds full `security.*` names for each LSM-provided xattr.
- Clears the negative capability-xattr cache when initializing `security.capability`.
- Inserts each xattr with `btrfs_setxattr()`.

## Error Handling and Edge Cases
- Missing xattr returns `-ENODATA`; oversized destination buffer returns `-ERANGE`.
- Allocation failures return `-ENOMEM`.
- Oversized xattr payloads return `-ENOSPC`.
- Transaction failures during inode update abort the transaction.
- `btrfs_listxattr()` supports size-query mode and stops with `-ERANGE` if the provided buffer is too small.

## Cross-File Links
Uses:
- `dir-item.c/.h` xattr lookup/insert/delete/matching helpers.
- `transaction.h` for transaction start/end.
- `props.h` for Btrfs property validation/application.
- `accessors.h` for leaf item access.
- `locking.h` for inode-lock assertions.
