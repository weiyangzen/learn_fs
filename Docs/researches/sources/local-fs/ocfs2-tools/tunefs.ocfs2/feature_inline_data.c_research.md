# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_inline_data.c

## Purpose
Enables or disables inline data support.

## Main Behavior
- Enable:
  - No-ops if already supported.
  - Prompts, sets `OCFS2_FEATURE_INCOMPAT_INLINE_DATA`, writes superblock.
- Disable:
  - Scans regular files and directories with `OCFS2_INLINE_DATA_FL`.
  - Counts one additional cluster per inline-data inode and verifies free space.
  - Converts each inline-data inode to extent-backed storage with `ocfs2_convert_inline_data_to_extents()`.
  - Loads quota info and applies quota usage changes for non-system files and the root inode.
  - Clears the inline-data incompat bit and writes the superblock.

## Dependencies
- `tunefs_foreach_inode()` and `tunefs_get_free_clusters()`.
- OCFS2 cached inode, inline conversion, quota change APIs.
- Kernel list helpers.

## Notes
Disable is a data migration. It requires enough free clusters to expand all inline data and updates quota accounting for cluster changes.
