# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_sparse_files.c

## Purpose
Enables or disables sparse file support.

## Main Behavior
- Enable:
  - Scans regular non-system, non-inline files and truncates allocations beyond `i_size`.
  - Sets `OCFS2_FEATURE_INCOMPAT_SPARSE_ALLOC`.
  - Writes the superblock.
- Disable:
  - Refuses to proceed if unwritten extents are enabled.
  - Scans regular non-system, non-inline files.
  - Records holes inside `i_size`, files requiring truncate-to-size, hole counts, needed data clusters, and estimated extent-block clusters.
  - Verifies free space can fill all holes and metadata needs.
  - Allocates clusters for each hole, zeroes them, inserts extents, and optionally truncates tail allocation.
  - Applies quota changes when cluster counts change.
  - Clears the sparse allocation feature and writes the superblock.

## Dependencies
- OCFS2 extent lookup/insertion, allocation, truncate, quota, and cached inode APIs.
- Tunefs inode scanning, free-space checks, and zero-fill helper.
- Kernel list helpers.

## Notes
Disable converts sparse holes into real zero-filled extents. It explicitly rejects sparse disable while unwritten extents remain enabled.
