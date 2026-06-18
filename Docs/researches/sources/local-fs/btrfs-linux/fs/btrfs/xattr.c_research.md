# File Research: sources/local-fs/btrfs-linux/fs/btrfs/xattr.c

This file implements Btrfs extended-attribute get, set, remove, list, VFS xattr handler dispatch, Btrfs property xattrs, and security xattr initialization.

Main exported functions:
- `btrfs_getxattr()` looks up a `BTRFS_XATTR_ITEM_KEY` dir item by inode objectid and full xattr name. It returns the value length for size queries, `-ERANGE` when the caller buffer is too small, copies the value from the leaf item when possible, and returns `-ENODATA` for missing xattrs.
- `btrfs_setxattr()` mutates an xattr inside an existing transaction. It enforces `BTRFS_MAX_XATTR_SIZE()`, handles removal when `value == NULL`, supports `XATTR_CREATE` and `XATTR_REPLACE`, inserts new dir items, and atomically replaces packed dir-item values.
- `btrfs_setxattr_trans()` wraps `btrfs_setxattr()` in a transaction when the caller does not already have one, reserves units for xattr and inode updates, updates inode ctime and i_version, writes the inode item, and aborts the transaction on update failure.
- `btrfs_listxattr()` walks all `BTRFS_XATTR_ITEM_KEY` items for an inode, iterates packed `struct btrfs_dir_item` entries inside each item, and either reports total list size or copies nul-terminated names into the caller buffer.
- `btrfs_xattr_security_init()` calls `security_inode_init_security()` with `btrfs_initxattrs()` to install initial LSM-provided security attributes during inode creation.

Mutation behavior:
- Removal uses `btrfs_lookup_xattr()` and `btrfs_delete_one_dir_name()`.
- Replace first performs a read-only lookup to ensure existence, relying on VFS inode locking to avoid racing with deletion.
- Insert uses `btrfs_insert_xattr_item()`.
- `-EOVERFLOW` from insertion means an existing leaf item could not be expanded by split logic; the code checks whether the target name exists and either replaces or returns `-ENOSPC`.
- `-EEXIST` means a matching xattr exists in the packed item and should be replaced unless `XATTR_CREATE` was requested.
- Replacement preserves atomic visibility: readers should see either the old or new value, not a transient missing value. If the xattr is alone in the item, the item is extended or truncated in place; if multiple xattrs are packed together, the old entry is deleted and a new entry is appended.

VFS xattr handlers:
- `btrfs_security_xattr_handler` handles `security.*` xattrs with capability-specific caching.
- `btrfs_trusted_xattr_handler` handles `trusted.*`.
- `btrfs_user_xattr_handler` handles `user.*`.
- `btrfs_btrfs_xattr_handler` handles `btrfs.*` property xattrs by validating and setting properties through `props.c`.
- `btrfs_xattr_handlers[]` exposes the handler array to the superblock/inode setup code.

Security/capability cache:
- `btrfs_xattr_handler_get_security()` caches missing `security.capability` by setting `BTRFS_INODE_NO_CAP_XATTR` after `-ENODATA`.
- `btrfs_xattr_handler_set_security()` clears `BTRFS_INODE_NO_CAP_XATTR` before changing `security.capability`.
- `btrfs_initxattrs()` also clears the capability-missing bit when initializing `security.capability`.

Property xattrs:
- `btrfs_xattr_handler_set_prop()` expands the handler/name pair to a full name, validates it with `btrfs_validate_prop()`, ignores properties that `btrfs_ignore_prop()` says should be ignored, starts a transaction, calls `btrfs_set_prop()`, and updates inode ctime/i_version plus the inode item.

Cross-file relationships:
- Uses `dir-item.c` helpers for xattr lookup, insertion, deletion, name matching, and leaf item packing.
- Uses `transaction.c` for start/end/abort transaction handling.
- Uses `props.c` for `btrfs.*` property validation and persistence.
- Uses inode runtime flags from `btrfs_inode.h`.
- Exposes declarations through `xattr.h`.
- Called through VFS xattr handler hooks registered by Btrfs inode/superblock operations.

Important invariants and risks:
- `btrfs_setxattr()` requires a valid transaction handle and asserts it.
- Xattr names stored here are full names including prefixes such as `security.`, `trusted.`, `user.`, or `btrfs.`.
- The total name plus value size must fit inside `BTRFS_MAX_XATTR_SIZE()`.
- Replace semantics are intentionally atomic for ACL and security correctness.
- On successful xattr mutation, `BTRFS_INODE_COPY_EVERYTHING` is set and `BTRFS_INODE_NO_XATTRS` is cleared.
- Root readonly checks happen in handler-level set paths before starting normal xattr/property transactions.
- `btrfs_setxattr_trans()` can reuse `current->journal_info` for nested security xattr initialization, notably Smack transmute xattrs during directory creation.
- `btrfs_initxattrs()` enters a NOFS allocation context while holding a transaction to reduce reclaim deadlock risk.
