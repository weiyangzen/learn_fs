# File Research: sources/os/linux/linux/fs/ocfs2/acl.c

## Role

Implements OCFS2 POSIX ACL conversion, retrieval, setting, chmod updates, and new-inode ACL initialization. ACLs are stored as OCFS2 xattrs and coordinated with OCFS2 inode locks, xattr semaphores, and journal transactions.

## Major Functions

- ACL serialization:
  - `ocfs2_acl_from_xattr()` converts little-endian OCFS2 ACL xattr entries to `struct posix_acl`.
  - `ocfs2_acl_to_xattr()` converts `struct posix_acl` back to OCFS2 xattr format.
- ACL lookup:
  - `ocfs2_get_acl_nolock()` maps ACL type to OCFS2 xattr index, queries xattr size, reads value, and converts it to a POSIX ACL.
- Mode update:
  - `ocfs2_acl_set_mode()` updates inode mode both in memory and on disk.
  - It can read its own inode block and start its own transaction if the caller does not provide them.
  - Journals dinode access, updates ctime, marks fsync transaction state, and dirties the buffer.
- ACL setting:
  - `ocfs2_set_acl()` validates symlink/default ACL rules, serializes ACLs, and writes/removes ACL xattrs either through an existing journal handle or the generic xattr setter.
  - Updates the VFS ACL cache on success.
- VFS inode operations:
  - `ocfs2_iop_set_acl()` obtains an inode lock, updates mode for access ACLs with `posix_acl_update_mode()`, writes the mode to disk, then writes the ACL xattr.
  - `ocfs2_iop_get_acl()` rejects RCU lookup, checks mount ACL option, locks inode, takes `ip_xattr_sem`, reads ACL, and releases locks.
- chmod handling:
  - `ocfs2_acl_chmod()` reads access ACL, applies mode changes with `__posix_acl_chmod()`, then writes the updated ACL.
- New inode initialization:
  - `ocfs2_init_acl()` reads parent default ACL if ACL mount option is enabled.
  - If no inherited ACL exists, applies current umask to mode.
  - If inherited ACL exists, writes default ACL for directories, derives access ACL/mode with `__posix_acl_create()`, persists mode, and writes access ACL when needed.

## Important Invariants

- Symlinks do not support ACL setting/chmod ACL updates.
- Default ACLs only apply to directories; non-directory default ACL removal is a no-op, but setting one returns `-EACCES`.
- ACL xattr names are represented by OCFS2 xattr indexes with empty names.
- Disk mode and in-memory mode are kept synchronized through journaling.
- ACL access paths must coordinate inode cluster locks and `ip_xattr_sem`.
- RCU ACL lookup is unsupported and returns `-ECHILD`.

## Dependencies

- OCFS2 internals: inode locks, dinode buffers, journal access, xattr get/set, allocation contexts, masklog, superblock mount options.
- Linux POSIX ACL helpers and ID mapping through `init_user_ns` / `nop_mnt_idmap`.
- `acl.h` for `struct ocfs2_acl_entry` and prototypes.

## Notes For Future Work

- The file credits ext3 ACL code lineage, so behavior tracks older filesystem ACL conventions.
- The conversion functions use `sizeof(struct posix_acl_entry)` for on-disk entry sizing while casting to `struct ocfs2_acl_entry`; these sizes match the local OCFS2 entry layout expectation.
- `ocfs2_iop_set_acl()` uses `nop_mnt_idmap` in `posix_acl_update_mode()`, so idmapped mount behavior should be considered if OCFS2 idmap support changes.
