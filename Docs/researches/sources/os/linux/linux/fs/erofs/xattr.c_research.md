# File Research: sources/os/linux/linux/fs/erofs/xattr.c

## Purpose
Implements EROFS extended-attribute initialization, lookup, listing, long-prefix support, POSIX ACL retrieval, and inode-share fingerprint extraction.

## Main Elements
- Iterator state: `struct erofs_xattr_iter` carries metadata buffers, current position, output buffer state, lookup name/index, and listing dentry.
- Per-inode xattr initialization: `erofs_init_inode_xattrs()` reads the xattr ibody header, name filter, shared-xattr count, and shared xattr ID array once per inode using bit locks and memory barriers.
- Entry walking helpers: `erofs_xattr_copy_to_buffer()`, `erofs_listxattr_foreach()`, and `erofs_getxattr_foreach()` process possibly block-crossing xattr entries, names, values, and long prefix infixes.
- Inline and shared xattr scans: `erofs_xattr_iter_inline()` walks inode-local xattrs, while `erofs_xattr_iter_shared()` resolves shared xattrs from the superblock xattr area, including optional metabox storage.
- Public operations: `erofs_getxattr()` uses an xxhash name filter shortcut when valid, then searches inline and shared xattrs; `erofs_listxattr()` emits listable names with prefixes.
- VFS xattr handlers: user, trusted, and optional security handlers are exposed through `erofs_xattr_handlers`, with user xattrs controlled by mount options and trusted xattrs controlled by `CAP_SYS_ADMIN`.
- Long-prefix lifecycle: `erofs_xattr_prefixes_init()` reads variable-sized long-prefix metadata and prepares inode-share prefix strings; `erofs_xattr_prefixes_cleanup()` frees them.
- Optional features: `erofs_get_acl()` reads POSIX ACL xattrs, `erofs_inode_has_noacl()` uses the xattr name filter as a fast no-ACL check, and `erofs_xattr_fill_inode_fingerprint()` builds page-cache sharing fingerprints from configured xattrs plus domain ID.

## Dependencies And Integration
Integrates with EROFS metadata buffers, inode layout fields, superblock xattr prefix state initialized by `super.c`, Linux VFS xattr handlers, POSIX ACL conversion, security xattrs, xxhash filtering, and optional page-cache sharing.

## Risk Notes
Corruption checks around `xattr_isize`, shared counts, entry sizes, and prefix lengths are critical because metadata can cross block boundaries. The initialized bit is paired with memory barriers so readers do not observe partially filled xattr fields. The name-filter optimization must be disabled when reserved format bits indicate incompatible filter semantics.
