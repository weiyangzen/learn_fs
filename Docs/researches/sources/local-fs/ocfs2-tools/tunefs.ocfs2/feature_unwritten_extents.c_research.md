# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_unwritten_extents.c

## Purpose
Enables or disables unwritten extent support.

## Main Behavior
- Enable:
  - No-ops if already enabled.
  - Requires sparse files to be enabled; otherwise returns `TUNEFS_ET_SPARSE_MISSING`.
  - Sets `OCFS2_FEATURE_RO_COMPAT_UNWRITTEN` and writes the superblock.
- Disable:
  - Scans regular, non-system, non-inline files.
  - For each extent marked `OCFS2_EXT_UNWRITTEN`, verifies/zero-checks the physical clusters through `tunefs_empty_clusters()`, then marks the extent written with `ocfs2_mark_extent_written()`.
  - Clears the RO-compatible feature and writes the superblock.

## Dependencies
- OCFS2 extent lookup and mark-written APIs.
- Tunefs inode scanning and zero-fill helper.

## Notes
Disable turns every unwritten extent into a written extent before clearing feature support.
