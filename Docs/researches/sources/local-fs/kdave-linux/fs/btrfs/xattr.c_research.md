# File Research: sources/local-fs/kdave-linux/fs/btrfs/xattr.c

## Role

`xattr.c` implements Btrfs extended attribute get/set/list operations and VFS xattr handlers for `security.*`, `trusted.*`, `user.*`, and `btrfs.*` property-backed attributes.

## Main Functions

- `btrfs_getxattr()` looks up a `BTRFS_XATTR_ITEM_KEY` dir item by inode and name, returns the stored data length for size probes, validates buffer size, then copies xattr data from the leaf.
- `btrfs_setxattr()` inserts, replaces, or deletes an xattr within an existing transaction. It enforces `BTRFS_MAX_XATTR_SIZE`, honors `XATTR_CREATE` and `XATTR_REPLACE`, and handles packed dir-item replacement atomically.
- `btrfs_setxattr_trans()` starts or reuses a transaction, calls `btrfs_setxattr()`, updates inode version/ctime, and persists the inode item.
- `btrfs_listxattr()` walks all xattr items for an inode and emits NUL-terminated names, or returns the required total size.
- Handler wrappers adapt Btrfs operations to Linux `xattr_handler` callbacks.
- `btrfs_initxattrs()` initializes security xattrs during inode creation under a supplied transaction.
- `btrfs_xattr_security_init()` delegates inode security initialization to LSM code with the Btrfs callback.

## Storage Model

Btrfs stores xattrs as dir items in the tree. A leaf item may pack multiple `struct btrfs_dir_item` entries. Each packed entry is laid out as:

`struct btrfs_dir_item` + xattr name + xattr data

Replacement must preserve atomic visibility. If the matched xattr is alone in the item, the item is extended or truncated in place. If other xattrs share the same item, the old dir-name entry is deleted and a new entry-sized region is added before writing the replacement value.

## Security and Properties

`security.capability` gets special negative-result caching through `BTRFS_INODE_NO_CAP_XATTR`, reducing repeated lookups for absent capability xattrs. Setting capability clears that cache bit.

`btrfs.*` xattrs are routed through property validation and `btrfs_set_prop()`, not generic xattr storage alone. Ignored properties are accepted as no-ops.

## Transaction and Locking Notes

`btrfs_setxattr_trans()` normally starts a two-unit transaction: one unit for xattr mutation and one for inode update. If already inside a transaction, it reuses `current->journal_info`; the documented case is SMACK security xattr setup during directory creation.

For `XATTR_REPLACE`, the code asserts the inode lock is held, first performs a read-only lookup, then releases the path before the insert/replace path.

## Side Effects

Successful set/delete operations set `BTRFS_INODE_COPY_EVERYTHING` and clear `BTRFS_INODE_NO_XATTRS`. Inode ctime and i_version are updated by the transaction wrapper and property path.
