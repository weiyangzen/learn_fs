# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_indexed_dirs.c

## Purpose
Enables or disables directory indexing.

## Main Behavior
- Enable:
  - Seeds `s_uuid_hash` if xattr is not enabled.
  - Generates three random `s_dx_seed` values.
  - Sets `OCFS2_FEATURE_INCOMPAT_INDEXED_DIRS`.
  - Writes the superblock.
  - Scans all valid inodes.
  - For each directory, truncates any stale indexed tree, installs directory trailers, then builds a dx/index tree.
- Disable:
  - Scans all directories with `OCFS2_INDEXED_DIR_FL` into a list.
  - Truncates each indexed tree with `ocfs2_dx_dir_truncate()`.
  - Clears the indexed dirs feature.
  - Clears `s_uuid_hash` only if xattr is not using it.
  - Clears `s_dx_seed[]`.
  - Writes the superblock.
- Defines `indexed_dirs_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Dependencies
- `tunefs_foreach_inode()`.
- Directory trailer helpers from `libocfs2ne.c`.
- OCFS2 dx directory APIs.
- Kernel list helpers.

## Notes
Disable intentionally clears the feature even if truncation encountered work already done; comments state `fsck.ocfs2` handles orphan indexed trees after touched filesystem state.
