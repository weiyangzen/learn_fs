# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.h

## Purpose

Declares kernel-only bmap utility APIs.

## Key Contents

- Realtime allocation API:
  - `xfs_bmap_rtalloc` or corruption stub when realtime is disabled.
- Delalloc cleanup:
  - `xfs_bmap_punch_delalloc_range`
- `getbmap` output:
  - `struct kgetbmap`
  - `xfs_getbmap`
- Bmap internal helpers used by utilities:
  - extsize alignment
  - adjacency
  - last extent lookup
- Preallocation and hole manipulation:
  - `xfs_alloc_file_space`
  - `xfs_free_file_space`
  - `xfs_collapse_file_space`
  - `xfs_insert_file_space`
- EOF block cleanup:
  - `xfs_can_free_eofblocks`
  - `xfs_free_eofblocks`
- Extent swap:
  - `xfs_swap_extents`
- Address conversion and counting:
  - `xfs_fsb_to_db`
  - `xfs_bmap_count_leaves`
  - `xfs_bmap_count_blocks`
  - `xfs_flush_unmap_range`

## Research Notes

This header is the public interface for higher-level XFS file operations that need extent manipulation without using raw bmap internals directly.
