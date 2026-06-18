# File Research: sources/os/linux/linux/fs/f2fs/xattr.c

Implements F2FS extended attribute handlers, xattr lookup/read/write/list/set operations, security xattr initialization, and the inline xattr slab cache.

Key behavior:
- Defines handlers for `user.*`, `trusted.*`, `security.*`, and F2FS `system.advise`.
- `user.*` xattrs are gated by the `XATTR_USER` mount option.
- `trusted.*` listing requires `CAP_SYS_ADMIN`.
- `system.advise` reads and updates `F2FS_I(inode)->i_advise`, allowing only owner/capable writers and only modifiable advise bits.
- Security xattrs are initialized through `security_inode_init_security()` when `CONFIG_F2FS_FS_SECURITY` is enabled.
- Maintains handler maps for VFS xattr dispatch and prefix filtering in `listxattr`.
- Allocates the common inline-xattr buffer size from `inline_xattr_slab`; larger temporary xattr buffers use `f2fs_kzalloc()`.
- Supports xattrs split across:
  - inline xattr space inside the inode node page
  - one external xattr node block referenced by `F2FS_I(inode)->i_xattr_nid`
- `__find_xattr()` iterates xattr entries with boundary checks against the valid buffer end and can report the last valid address for inline/external searches.
- `lookup_all_xattrs()` reads inline xattrs first, then the xattr node block if present, searches for the requested entry, detects corrupted layouts, marks `SBI_NEED_FSCK`, and calls `f2fs_handle_error(ERROR_CORRUPTED_XATTR)`.
- `read_all_xattrs()` builds a complete temporary xattr image, initializes a missing header with `F2FS_XATTR_MAGIC`, and supports empty xattr state.
- `write_all_xattrs()` writes the temporary xattr image back:
  - Allocates a new xattr node nid if needed.
  - Updates inline xattr space when present.
  - Truncates the xattr node if the new xattr set fits inline.
  - Writes or creates the external xattr node block when needed.
  - Marks affected folios dirty and handles nid allocation success/failure.
- `f2fs_getxattr()` validates name length, takes `i_xattr_sem` unless using a caller-provided inode folio, looks up the entry, validates buffer size and in-buffer bounds, copies the value, and returns the value size.
- `f2fs_listxattr()` reads all xattrs, filters entries by handler/list permissions, emits prefixed names, detects corrupt entry boundaries, and returns required/used buffer size.
- `__f2fs_setxattr()` handles create/replace/delete/update semantics:
  - Validates name and maximum value length.
  - Reads all xattrs and searches for the target entry.
  - Attempts xattr recovery if corruption is found and no xattr node exists.
  - Enforces `XATTR_CREATE`/`XATTR_REPLACE`.
  - Skips rewriting identical values.
  - Checks free space before insertion.
  - Removes old entries with `memmove()`.
  - Writes a new aligned entry and explicit null terminator.
  - Persists with `write_all_xattrs()`.
  - Sets encrypted inode state when the encryption context xattr is written.
  - For directory xattr changes, requests checkpoint or records `XATTR_DIR_INO` depending on fsync mode.
  - Restores ACL mode state when `FI_ACL_MODE` is set.
  - Updates ctime and marks the inode dirty.
- `f2fs_setxattr()` checks checkpoint/error readiness, initializes quota, supports the metadata-initialization fast path with caller-provided folio, otherwise balances FS, takes the global F2FS operation lock and inode xattr write semaphore, calls the internal setter, unlocks, and updates request time.
- Initializes and destroys the `f2fs_xattr_entry` slab cache used for default inline xattr temporary buffers.

Important interactions:
- Used by VFS xattr operations through `f2fs_xattr_handlers`, by fscrypt for encryption contexts, by fs-verity for descriptor-location xattrs, by security initialization, and by inode metadata creation.
- Corruption detection feeds into `SBI_NEED_FSCK` and F2FS critical error handling.
- The inline/external split is defined by `xattr.h` macros and by inode feature layout.
