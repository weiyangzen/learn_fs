# File Research: sources/os/linux/linux/fs/ext2/xattr.c

## Purpose
Implements ext2 extended attribute storage, lookup, listing, mutation, sharing, hashing, cache management, and inode cleanup.

## Main Responsibilities
- Stores xattrs in a single external EA block referenced by `EXT2_I(inode)->i_file_acl`.
- `ext2_xattr_get()` validates the EA block and entries, finds the sorted name/index entry, and copies or sizes the value.
- `ext2_xattr_list()` validates the block, filters namespace visibility through handlers, and emits prefixed names.
- `ext2_xattr_set()` creates, replaces, or removes attributes, preserving sorted entries and compact value layout.
- `ext2_xattr_set2()` updates inode state, reuses identical cached blocks, allocates new EA blocks, releases old blocks, updates quotas, and marks metadata dirty.
- `ext2_xattr_delete_inode()` releases the inode’s EA block on inode deletion.
- Hash and mbcache helpers enable sharing identical EA blocks by content hash and refcount.

## Integration Points
Uses ext2 block allocation/freeing, quota initialization/accounting, buffer-head IO, superblock feature updates, `mb_cache`, namespace handlers from user/trusted/security/ACL code, and inode xattr semaphores.

## Important Behaviors
EA blocks are copy-on-write unless exclusively owned and not being reused. The code validates magic, block count, entry boundaries, value offsets, and unsupported external value blocks. Setting the first xattr upgrades the superblock to dynamic revision and sets `EXT2_FEATURE_COMPAT_EXT_ATTR`.

## Risks and Edge Cases
Locking is delicate: inode `xattr_sem` protects `i_file_acl`, buffer locks serialize shared block refcount/content changes, and mbcache races are handled with delete-or-get/wait paths. Corrupt xattr blocks trigger `ext2_error()`. Attribute size is limited by filesystem block size.
