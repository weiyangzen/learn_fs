# File Research: sources/os/linux/linux-stable/fs/erofs/xattr.c

This file implements EROFS extended-attribute lookup, listing, long-prefix loading, POSIX ACL extraction, and page-cache-share fingerprint generation.

Major responsibilities:
- Lazily initializes each inode’s xattr metadata in `erofs_init_inode_xattrs()`, loading the ibody header, name filter, shared-xattr count, and shared-xattr id array.
- Iterates inline xattrs stored after the inode body and shared xattrs stored in the global xattr area.
- Implements `erofs_getxattr()` and `erofs_listxattr()` using `struct erofs_xattr_iter`.
- Supports long xattr prefixes through superblock-level prefix tables loaded by `erofs_xattr_prefixes_init()`.
- Provides VFS xattr handlers for `user.*`, `trusted.*`, and, when enabled, `security.*`.
- Implements POSIX ACL lookup with `erofs_get_acl()` and a fast xattr-filter helper `erofs_inode_has_noacl()`.
- Implements inode-share fingerprint extraction with `erofs_xattr_fill_inode_fingerprint()` when page-cache sharing is enabled.

Important data flow:
- `erofs_init_inode_xattrs()` uses `EROFS_I_BL_XATTR_BIT` as a bit lock and `EROFS_I_EA_INITED_BIT` as the published initialized state.
- Memory barriers pair the initialized bit with loaded inode fields so other threads do not observe partially initialized xattr state.
- Inline iteration walks entries within `vi->xattr_isize`; shared iteration maps global xattr entries by id relative to `sbi->xattr_blkaddr`.
- `getxattr` can use the on-disk xxhash name filter to reject definitely absent names without scanning entries.
- Long-prefix entries match both the stored prefix base index and the dynamic infix before comparing the rest of the xattr name.

Validation and error handling:
- Missing xattrs return `-ENODATA`; absent lists become length zero.
- Malformed ibody sizes, shared counts, overlong names, malformed prefix lengths, and entry sizes extending beyond `xattr_isize` return corruption or range errors.
- User xattrs honor the `XATTR_USER` mount option.
- Trusted xattrs are listable only by `CAP_SYS_ADMIN`.
- POSIX ACL RCU lookup returns `-ECHILD`, forcing non-RCU lookup.

External interfaces:
- Exports `erofs_xattr_handlers`, `erofs_listxattr()`, `erofs_xattr_prefixes_init()`, `erofs_xattr_prefixes_cleanup()`, and optional ACL/fingerprint helpers.
