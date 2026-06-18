# File Research: sources/os/linux/linux-stable/fs/btrfs/xattr.c

## Purpose

`xattr.c` implements Btrfs extended attribute get, set, remove, list, VFS xattr handlers, Btrfs property xattrs, and inode security-label initialization.

## Main Functions

- `btrfs_getxattr()`
  - Looks up a `BTRFS_XATTR_ITEM_KEY` dir item by inode/object id and name.
  - Returns the value size when caller passes size 0.
  - Copies packed dir-item xattr data from the leaf into the caller buffer.
  - Returns `-ENODATA`, `-ERANGE`, or lookup errors as appropriate.

- `btrfs_setxattr()`
  - Requires an active transaction.
  - Enforces `BTRFS_MAX_XATTR_SIZE`.
  - Treats `value == NULL` as removal.
  - Honors `XATTR_CREATE` and `XATTR_REPLACE`.
  - Handles packed xattrs in a single item, including atomic replacement.
  - Updates inode runtime flags: sets `BTRFS_INODE_COPY_EVERYTHING` and clears `BTRFS_INODE_NO_XATTRS` on success.

- `btrfs_setxattr_trans()`
  - Starts a transaction unless one already exists in `current->journal_info`.
  - The existing-transaction path supports security modules setting xattrs during inode creation.
  - Updates inode version, ctime, and inode item after successful xattr update.

- `btrfs_listxattr()`
  - Iterates all xattr keys for the inode.
  - Walks packed `struct btrfs_dir_item` records inside each item.
  - Computes required buffer size or copies null-terminated names.
  - Returns `-ERANGE` when the caller buffer is too small.

- VFS handlers:
  - security, trusted, user, and Btrfs property namespaces are registered in `btrfs_xattr_handlers`.
  - security capability lookups use `BTRFS_INODE_NO_CAP_XATTR` as a negative cache.
  - `btrfs.*` xattrs route through property validation and `btrfs_set_prop()`.

- `btrfs_xattr_security_init()`
  - Calls `security_inode_init_security()` with `btrfs_initxattrs()`.
  - `btrfs_initxattrs()` builds full `security.*` names and writes them in a NOFS allocation context.

## Important Details

- Xattrs are stored using Btrfs dir-item packing: `struct btrfs_dir_item`, name bytes, then value bytes.
- Replacement is designed to be atomic from readers’ perspective, particularly for ACLs.
- When replacing an xattr packed with other xattrs in the same item, the code deletes only the matching dir name and then extends the item for the new value.
- Read-only roots reject set operations with `-EROFS`.
- Property xattrs can be ignored by `btrfs_ignore_prop()` after validation.
- Transaction abort is triggered when inode update fails after xattr/property mutation.

## Dependencies

This file depends on VFS xattr/security APIs, POSIX ACL xattr names, inode versioning, Btrfs transaction handling, dir-item helpers, tree locking, property validation, inode update, and extent-buffer accessors.

## Research Notes

This implementation is tightly coupled to Btrfs dir-item packing and transaction semantics. The main invariants are maximum xattr item size, correct create/replace/remove error behavior, atomic replacement visibility, and keeping inode metadata/runtime flags synchronized after successful changes.
