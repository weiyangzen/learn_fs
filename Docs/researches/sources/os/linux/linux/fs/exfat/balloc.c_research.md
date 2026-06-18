# File Research: sources/os/linux/linux/fs/exfat/balloc.c

## Purpose
Manages the exFAT allocation bitmap: loading it from disk, querying and mutating cluster allocation bits, counting used clusters, finding free clusters, and issuing discard ranges for FITRIM.

## Main Interfaces
- `exfat_load_bitmap`, `exfat_free_bitmap`
- `exfat_set_bitmap`, `exfat_clear_bitmap`, `exfat_test_bitmap`
- `exfat_find_free_bitmap`, `exfat_count_used_clusters`
- `exfat_trim_fs`

## Key Data Flow
`exfat_load_bitmap()` scans root directory entries for the primary allocation bitmap entry, then `exfat_allocate_bitmap()` validates the advertised bitmap size, allocates `sbi->vol_amap`, reads all bitmap sectors, and verifies that clusters backing the bitmap itself are marked allocated. Set/clear/test functions translate cluster numbers through `CLUSTER_TO_BITMAP_ENT()` and sector/bit macros from `exfat_fs.h`.

`exfat_find_free_bitmap()` searches little-endian machine-word chunks, wraps at the end of the bitmap, and returns `EXFAT_EOF_CLUSTER` on exhaustion. `exfat_trim_fs()` walks free-cluster runs in the requested byte range and calls `sb_issue_discard()` for runs meeting `minlen`.

## Dependencies
Uses `struct exfat_sb_info` bitmap fields, root directory entry scanning via `exfat_get_dentry()`, endian-aware bitmap helpers, block readahead, buffer heads, and block-device discard APIs.

## Notable Invariants And Risks
- Bitmap size smaller than required is treated as I/O corruption.
- `exfat_clear_bitmap()` rejects clearing an already-free bit.
- `exfat_test_bitmap()` returns true if the bitmap is not loaded, allowing some callers to proceed during early mount/setup paths.
- Correct locking is expected around allocation/free callers; trim takes `bitmap_lock` itself.
