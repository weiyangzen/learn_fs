# File Research: sources/os/linux/linux-stable/fs/jfs/xattr.c

## Purpose

Implements JFS extended attributes: FEALIST parsing, inline/extent storage, namespace mapping, get/set/list operations, VFS xattr handlers, and security xattr initialization.

## Data Format And Storage

JFS stores a `struct jfs_ea_list` containing a 32-bit total size and a packed sequence of `struct jfs_ea` entries. Each entry contains flags, name length, 16-bit value length, a NUL-terminated name, and value bytes. Attribute lists may live inline in the inode (`DXD_INLINE`) or in allocated extents (`DXD_EXTENT`) accessed through metapages.

## Namespace Mapping

Unknown on-disk prefixes are presented to userspace with the `os2.` prefix. Known namespaces are `system.`, `user.`, `security.`, and `trusted.`. The OS/2 xattr handler rejects known namespace names so it only covers legacy/unknown names.

## Core Helpers

- `ea_write_inline()` writes a small or empty list into inode inline EA space when available and updates the DXD descriptor.
- `ea_write()` chooses inline storage or allocates blocks with quota charging and `dbAlloc()`, writes metapages synchronously, and fills the new DXD.
- `ea_read_inline()` and `ea_read()` load an EA list from inode inline data or extent metapages.
- `ea_get()` returns a mutable buffer for current EAs, allocating a larger inline/extent/kmalloc buffer when the caller needs room for updates. It validates the list size and dumps bad EA contents before returning `-EIO`.
- `ea_release()` releases or rolls back buffers, including freeing newly allocated extent blocks if the update is abandoned.
- `ea_put()` commits a new EA descriptor through `txEA()`, invalidates old extent metapages, frees old quota blocks, updates inode ctime, and frees inline space when appropriate.

## Public Operations

- `__jfs_setxattr()` serializes with `xattr_sem`, reads current EAs, enforces create/replace semantics, removes an existing matching entry, validates that values fit in the on-disk 16-bit field, appends the new entry, and calls `ea_put()`.
- `__jfs_getxattr()` serializes with `xattr_sem`, walks the FEALIST with corruption bounds checks, and returns the value size or bytes.
- `jfs_listxattr()` lists names, hiding `trusted.*` without `CAP_SYS_ADMIN` and applying the OS/2 prefix mapping.
- `__jfs_xattr_set()` wraps setxattr in a JFS transaction and inode `commit_mutex`.
- Handler tables wire `user`, `os2`, `security`, and `trusted` namespaces into VFS xattr dispatch.
- With `CONFIG_JFS_SECURITY`, `jfs_init_security()` stores LSM-provided security xattrs during inode creation using the existing transaction.

## Notes

The implementation carefully separates allocated-but-uncommitted EA buffers from existing committed EA storage. Value length is rejected at `>= USHRT_MAX` to avoid overflowing the on-disk 16-bit length. Extent allocation failure paths roll back quota and block allocation.
