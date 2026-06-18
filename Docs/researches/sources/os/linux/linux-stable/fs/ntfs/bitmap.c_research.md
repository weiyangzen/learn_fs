# File Research: sources/os/linux/linux-stable/fs/ntfs/bitmap.c

Purpose: NTFS bitmap manipulation and filesystem trim support.

Key responsibilities:
- `ntfs_trim_fs()` scans the volume LCN bitmap for free cluster runs, aligns discard ranges to block-device discard granularity, issues `blkdev_issue_discard()`, and reports total trimmed bytes in `range->len`.
- `__ntfs_bitmap_set_bits_in_run()` sets or clears arbitrary bit ranges in a bitmap inode, spanning folios as needed, with rollback on later folio-mapping failure.

Important behavior:
- Bitmap bits are little-endian bit positions within bytes.
- Folios are read, locked, locally mapped, modified, marked dirty, unlocked, and put.
- For `FILE_Bitmap`, updates call `ntfs_set_lcn_empty_bits()` to keep volume free-space accounting or auxiliary empty-bit state in sync.
- Partial first/last bytes are handled bit-by-bit; full bytes are changed with `memset()`.
- Rollback recursively restores already-modified bits if a subsequent page fails to map.

Risk notes:
- Trim operates page-by-page over the bitmap and relies on zero bits meaning free clusters.
- Rollback failure marks the volume erroneous because metadata may be inconsistent.
- `WARN_ON(cnt > 7)` documents the expected final partial-byte invariant.
