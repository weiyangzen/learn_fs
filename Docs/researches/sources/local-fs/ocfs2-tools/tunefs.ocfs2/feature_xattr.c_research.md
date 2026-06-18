# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_xattr.c

## Purpose
Enables or disables extended attribute support.

## Main Behavior
- Enable:
  - No-ops if already enabled.
  - Sets `s_uuid_hash` if indexed dirs are not using it.
  - Sets `s_xattr_inline_size` to `OCFS2_MIN_XATTR_INLINE_SIZE`.
  - Sets `OCFS2_FEATURE_INCOMPAT_XATTR`.
  - Writes superblock.
- Disable:
  - Scans regular files, directories, and symlinks with `OCFS2_HAS_XATTR_FL`.
  - Removes inline xattr values, external xattr blocks, indexed xattr buckets, and xattr value trees.
  - Deletes external xattr blocks.
  - Adjusts inline-data capacity or extent-list count after inline xattr removal.
  - Clears per-inode xattr dynamic flags and `i_xattr_loc`.
  - Clears global xattr metadata fields and feature bit.
  - Writes superblock.

## Dependencies
- OCFS2 xattr block, bucket, tree, and value truncation APIs.
- Tunefs inode scanning and progress helpers.
- Kernel list helpers.

## Notes
Disable deletes all xattrs. It preserves `s_uuid_hash` if indexed directories still need it.
