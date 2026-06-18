# File Research: sources/os/linux/linux-stable/fs/ocfs2/acl.h

Purpose: Header for OCFS2 ACL on-disk entry layout and ACL operation prototypes.

Key contents:
- Defines `struct ocfs2_acl_entry` with little-endian tag, permission, and id fields.
- Declares VFS-facing ACL operations: `ocfs2_iop_get_acl()` and `ocfs2_iop_set_acl()`.
- Declares internal helpers: `ocfs2_acl_chmod()` and `ocfs2_init_acl()`.

Important invariants:
- On-disk ACL entries are little-endian and converted explicitly in `acl.c`.
- `ocfs2_init_acl()` requires caller-supplied journal handle, inode/parent inode, dinode buffers, and metadata/data allocation contexts.

Dependencies:
- Includes `linux/posix_acl_xattr.h`.
- Function signatures depend on OCFS2 buffer heads and allocation-context types from other OCFS2 headers included by users.
