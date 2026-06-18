# File Research: sources/os/linux/linux-stable/fs/ext4/fsmap.c

This file implements ext4’s `FS_IOC_GETFSMAP` support. It translates ext4 allocation and fixed metadata information into generic fsmap records for userspace.

Major responsibilities:
- Convert between generic byte-based `struct fsmap` and ext4 block-based `struct ext4_fsmap`:
  - `ext4_fsmap_from_internal()`
  - `ext4_fsmap_to_internal()`
- Drive getfsmap queries:
  - `ext4_getfsmap()` validates flags/devices/key ordering, prepares per-device query keys, sorts data/journal handlers by device ID, calls each matching handler, and sets `FMH_OF_DEV_T`.
- Report mappings:
  - `ext4_getfsmap_helper()` filters records before the low key, counts or formats entries, emits gaps as `EXT4_FMR_OWN_UNKNOWN`, emits real records, tracks `gfi_next_fsblk`, and supports abort when output is full.
- Data device mapping:
  - `ext4_getfsmap_datadev()` clamps keys to filesystem block bounds, computes start/end block groups, builds fixed metadata records, queries free-space ranges via `ext4_mballoc_query_range()`, merges fixed metadata with free extents, emits trailing retained free extents, and uses a dummy terminal record to flush end gaps.
  - `ext4_getfsmap_datadev_helper()` converts buddy free ranges into fsmap records and coalesces free extents across block group boundaries.
  - `ext4_getfsmap_meta_helper()` emits fixed metadata records that overlap the current query range.
- Journal device mapping:
  - `ext4_getfsmap_logdev()` fabricates a single mapping for an external journal device using `j_blk_offset` and `j_total_len`.
- Fixed metadata discovery:
  - `ext4_getfsmap_find_fixed_metadata()` collects superblocks, group descriptors, reserved GDT blocks, block bitmaps, inode bitmaps, and inode tables for all groups.
  - `ext4_getfsmap_find_sb()` records per-group superblock/GDT/reserved-GDT metadata.
  - `ext4_getfsmap_merge_fixed_metadata()` merges adjacent fixed metadata extents with the same owner.
  - `ext4_getfsmap_free_fixed_metadata()` releases temporary metadata lists.
- Validation and ordering:
  - `ext4_getfsmap_is_valid_device()` accepts the data device, optional external journal device, zero, and wildcard-style device values.
  - `ext4_getfsmap_check_keys()` enforces low-key ordering before query execution.
  - `ext4_getfsmap_dev_compare()` sorts handlers by encoded device number.

Important design points:
- ext4 does not have a full reverse-mapping tree, so fsmap output is synthesized from block allocator free-space data plus known fixed metadata; unknown gaps are reported explicitly.
- Fixed metadata is pre-collected and sorted so it can be interleaved with free-space callbacks.
- Free extents at block group ends are retained temporarily to merge with the next group if adjacent.
- The low key’s nonzero length is treated as a continuation cursor and advanced to avoid returning the same mapping twice.
- Data-device records use filesystem block units internally and are converted to bytes at the public boundary.

Key invariants:
- The formatter is called only until `fmh_count` entries are filled unless it aborts earlier.
- A count-only query has `fmh_count == 0` and increments `fmh_entries` without formatting records.
- `gfi_next_fsblk` is the monotonic cursor used to detect unreported allocated/unknown gaps.
- Metadata-list elements are freed as they become obsolete or at function exit.
