# File Research: sources/os/linux/linux/fs/ocfs2/xattr.h

Public OCFS2 xattr interface shared by the xattr implementation and the rest of OCFS2.

Key contents:
- Defines OCFS2 xattr namespace indexes for user, POSIX ACL access/default, trusted, security, and max sentinel.
- Defines `struct ocfs2_security_xattr_info`, the create-time carrier for LSM security xattr name/value data and enable state.
- Declares the OCFS2 user, trusted, and security `xattr_handler`s plus the handler table used by inode operation tables.
- Declares list/get/set/remove APIs, including `ocfs2_xattr_get_nolock()` for callers that already hold required locks and inode buffer state.
- Declares `ocfs2_xattr_set_handle()`, used during inode creation when the caller already owns a transaction and reserved allocators.
- Declares create-time sizing helpers `ocfs2_calc_security_init()` and `ocfs2_calc_xattr_init()`.
- Defines `struct ocfs2_xattr_value_buf`, a small wrapper that identifies the buffer head, journal access function, and value root for an external xattr value tree.
- Declares refcount/reflink helpers for attaching refcount trees, copying xattrs during reflink, and reinitializing security/ACL state.

Important contract:
- Xattrs may live in an inode, an external xattr block, or an indexed-tree bucket, but callers that operate on external value roots can use `ocfs2_xattr_value_buf` to avoid caring about the container.
