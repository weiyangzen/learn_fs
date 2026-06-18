# File Research: sources/os/linux/linux-stable/fs/exfat/balloc.c

This file manages the exFAT allocation bitmap: loading it from disk, testing/setting/clearing bits, finding free clusters, counting used clusters, and implementing FITRIM discard over free extents.

Key elements:
- Uses endian-aware word access helpers for 32-bit and 64-bit `BITS_PER_LONG`.
- `exfat_allocate_bitmap()` validates the bitmap dentry, computes expected bitmap size from `EXFAT_DATA_CLUSTER_COUNT()`, reads all bitmap sectors with readahead, and checks that the bitmap’s own clusters are allocated.
- `exfat_load_bitmap()` scans the root directory for the primary allocation bitmap entry with flag `0x0`.
- `exfat_set_bitmap()`, `exfat_clear_bitmap()`, and `exfat_test_bitmap()` manipulate little-endian allocation bits in `sbi->vol_amap`.
- `exfat_find_free_bitmap()` searches from a cluster hint and wraps to the beginning when reaching the end.
- `exfat_count_used_clusters()` counts set bits in the loaded allocation bitmap.
- `exfat_trim_fs()` translates an `fstrim_range` into cluster ranges, scans free clusters, and issues `sb_issue_discard()` for contiguous free runs at least `minlen`.

Important dependencies:
- Depends on `exfat_get_dentry()`, `exfat_get_entry_type()`, `exfat_get_next_cluster()`, and `exfat_blk_readahead()` for root directory scanning and bitmap I/O.
- `fatent.c` allocation/free code calls these bitmap helpers under `sbi->bitmap_lock`.
- Uses `exfat_cluster_to_sector()` and bitmap offset macros from `exfat_fs.h`.

Failure/edge behavior:
- Invalid cluster IDs are rejected before bitmap access.
- A bitmap smaller than required is fatal; a larger bitmap is tolerated.
- `exfat_clear_bitmap()` returns error if clearing an already-free bit.
- `exfat_test_bitmap()` returns true if `vol_amap` is absent, which avoids false failure before bitmap loading but means callers must ensure mount-time initialization happened.
