# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_bmap.c

## Purpose
Implements logical-to-physical block mapping for UFS, including direct and indirect block traversal, run-length clustering hints, sparse block handling, snapshot special cases, indirect logical block path construction, and `SEEK_DATA` support.

## Key Contents
- Sysctl:
  - `vfs.ufs.bmap_use_unmapped`
  - Controls whether UFS bmap may use unmapped buffers for indirect reads.
- Public bmap entry:
  - `ufs_bmap`
    - Supplies backing device bufobj if requested.
    - Uses `ufs_bmaparray` to translate logical block number to disk block number.
- Indirect block read helper:
  - `readindir`
    - Gets/caches indirect block buffers.
    - Can use `GB_UNMAPPED` for UFS2 when enabled.
    - Issues BIO read manually when buffer is not cached.
    - Updates RACCT and thread block I/O statistics.
- Unmapped buffer helpers:
  - `ufs_bm_sf_get`
  - `ufs_bm_sf_put`
    - Temporarily map buffer pages via `sf_buf` while CPU-pinned.
- Main mapping routine:
  - `ufs_bmaparray`
    - Calls `ufs_getlbns` to compute indirect path.
    - Handles direct blocks, UFS2 external attribute blocks, and indirect blocks.
    - Returns `-1` for holes unless snapshot semantics map them differently.
    - Treats snapshot sentinel blocks in range `1..um_seqinc` as zero-fill.
    - Validates indirect addresses via `UFS_CHECK_BLKNO`.
    - Calculates forward/backward contiguous run lengths for clustering.
    - Handles both UFS1 32-bit and UFS2 64-bit block pointer arrays.
- Logical block count helper:
  - `lbn_count`
    - Computes number of data blocks addressed by an indirect level.
- `SEEK_DATA` support:
  - `ufs_bmap_seekdata`
    - Rejects non-regular files and snapshots.
    - Validates requested offset against file size.
    - Calls `vnode_pager_clean_sync` so delayed dirty pages are reflected in block allocation.
    - Scans direct and indirect pointers for the next allocated data block.
    - Returns `ENXIO` if no data exists at or after the requested offset.
- Indirect path construction:
  - `ufs_getlbns`
    - Converts data or metadata logical block number into an array of `struct indir` entries.
    - Handles direct blocks, single/double/triple indirection, and negative metadata logical block numbers.
    - Returns `EFBIG` for out-of-range logical blocks.

## Interactions
- Uses `struct inode`, `DIP`, `I_IS_UFS1`, `I_IS_UFS2`, `IS_SNAPSHOT`.
- Depends on mount/ufsmount block-size helpers such as `MNINDIR`, `blkptrtodb`, `is_sequential`.
- Exposed through `ufs_extern.h`.
- Used by vnode paging, clustering, read/write, and seek-data paths.
