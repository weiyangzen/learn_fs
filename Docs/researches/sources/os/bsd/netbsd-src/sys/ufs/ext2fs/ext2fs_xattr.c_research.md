# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.c

This file implements read and list support for ext2 extended attributes. Setting and deleting attributes are present as VOP stubs returning `EOPNOTSUPP`.

Key responsibilities:
- Map ext2 xattr prefix indexes to visible attribute names.
- Find a named xattr in inline inode storage or an external xattr block.
- List xattr names from inline inode storage and external blocks.
- Enforce NetBSD extattr credential checks and offset restrictions.

Important functions:
- `xattr_prefix_index`: Prefix table for ext2 name indexes, including `user.`, POSIX ACL names, `trusted.`, `security`, `system.`, `system.richacl`, and encryption prefix.
- `ext2fs_find_xattr`: Iterates aligned xattr entries until the terminating entry or end bound. It filters USER vs SYSTEM namespace, matches prefix index and name, validates value bounds, optionally moves value bytes to `uio`, and reports full value size.
- `ext2fs_get_inode_xattr`: Locates inline xattrs after `EXT2_REV0_DINODE_SIZE + e2di_extra_isize`, validates magic, and searches entries.
- `ext2fs_get_block_xattr`: Reads the external xattr block from `e2di_facl` plus high bits on 64-bit filesystems, validates magic, and searches entries.
- `ext2fs_getextattr`: Checks credentials, rejects nonzero offsets, strips the longest matching known prefix from the requested name to derive ext2 name index/name, searches inline xattrs first, then the external block on `ENODATA`.
- `ext2fs_setextattr`: Not implemented; returns `EOPNOTSUPP`.
- `ext2fs_list_xattr`: Iterates entries and emits names with optional length prefix or trailing NUL.
- `ext2fs_list_inode_xattr` and `ext2fs_list_block_xattr`: List inline and external xattr entries respectively.
- `ext2fs_listextattr`: Checks `EXT2F_COMPAT_EXTATTR`, credentials, and zero offset; lists inline then block attributes and reports total size.
- `ext2fs_deleteextattr`: Not implemented; returns `EOPNOTSUPP`.

Important interactions:
- Vnode operation vectors in `ext2fs_vnops.c` expose get/set/list/delete xattr hooks for regular, special, and fifo vnodes.
- Uses on-disk structures and macros from `ext2fs_xattr.h`.
- Uses `extattr_check_cred` for namespace permission checks.

Notable behavior and risks:
- `ext2fs_get_block_xattr` returns success with size zero if there is no external block, but `ext2fs_getextattr` only calls it after inline lookup returns `ENODATA`; absent block therefore makes a missing attribute look like success with size zero. This should be checked against expected extattr semantics.
- In `ext2fs_find_xattr`, the code adjusts `uio_resid` before calling `uiomove(value, value_len, uio)` rather than passing the clipped length. The intent is to limit transfer by temporary resid, but this pattern is fragile.
- The prefix table entry for security is `"security"` while the header comment says `EXT2FS_XATTR_PREFIX_SECURITY` corresponds to `"security."`.
