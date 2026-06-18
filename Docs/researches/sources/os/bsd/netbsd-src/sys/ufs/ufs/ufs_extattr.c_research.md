# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extattr.c

This file implements UFS extended attributes using per-attribute backing files.

Key responsibilities:
- Manages per-mount extended attribute state and recursive mount-level locking.
- Autostarts attributes from `.attribute/system` and `.attribute/user`.
- Enables/disables attributes by opening backing vnodes and validating file headers.
- Autocreates backing files for supported namespaces when setting an unknown attribute.
- Implements vnode get, set, delete, and list extended-attribute operations.
- Removes all enabled attributes for an inode during inactive cleanup.
- Handles byte-swapped backing-file headers.

Storage model:
- Each enabled attribute has one backing file.
- Each inode maps to a fixed-size record in that backing file:
  `file header + inode_number * (attribute header + max attribute size)`.
- Per-record headers store in-use flag, length, and inode generation.

Important behavior:
- Attribute reads and writes require offset zero, enforcing replace-style semantics.
- Attribute data writes are not atomic with header writes.
- `ufs_extattr_sync` can force synchronous backing-file writes.
- Generation mismatch makes an attribute appear undefined.
- Access checks go through `extattr_check_cred`.
