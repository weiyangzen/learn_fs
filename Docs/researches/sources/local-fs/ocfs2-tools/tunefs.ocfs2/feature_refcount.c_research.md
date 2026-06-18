# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_refcount.c

## Purpose
Enables or disables refcount tree support.

## Main Behavior
- Enable:
  - No-ops if already enabled.
  - Prompts, sets `OCFS2_FEATURE_INCOMPAT_REFCOUNT_TREE`, writes superblock.
- Disable:
  - Scans regular non-system inodes with `OCFS2_HAS_REFCOUNT_FL`.
  - Groups files by `i_refcount_loc` in an rb-tree of refcount blocks.
  - Counts refcounted data and xattr clusters, estimating space needed to COW shared clusters and extra extent blocks.
  - Verifies enough free space.
  - For each file, calls `ocfs2_refcount_cow()` for data and COWs refcounted xattr value clusters.
  - Clears per-inode refcount dynamic feature and `i_refcount_loc`.
  - Verifies/refuses unexpected non-empty refcount tree state through assertions, then deletes empty refcount blocks.
  - Clears the incompat feature and writes the superblock.

## Dependencies
- OCFS2 rb-tree/list helpers.
- OCFS2 refcount, xattr iterate, cached inode, and extent APIs.
- Tunefs free-space and progress helpers.

## Notes
Disable is a full copy-on-write materialization pass. It needs enough free space to break sharing before the global feature bit can be cleared.
