# File Research: sources/os/linux/linux/fs/ext4/balloc.c

## Purpose
Implements ext4 block-group arithmetic, block bitmap initialization/validation/loading, free-cluster accounting, allocation retry policy, metadata block allocation wrapper, and metadata overhead calculations.

## Main Responsibilities
- `ext4_get_group_number()` and `ext4_get_group_no_and_offset()` map filesystem block numbers to groups and bitmap offsets.
- `ext4_num_overhead_clusters()` and related helpers compute per-group metadata overhead, including superblocks, group descriptors, bitmaps, and inode tables.
- `ext4_init_block_bitmap()` initializes uninitialized group block bitmaps and marks metadata/padding bits.
- `ext4_get_group_desc()` retrieves group descriptors from the RCU-managed descriptor buffer array.
- `ext4_read_block_bitmap_nowait()`, `ext4_wait_block_bitmap()`, and `ext4_read_block_bitmap()` load and verify block bitmaps.
- `ext4_validate_block_bitmap()` verifies checksums, required metadata bits, and padding bits, then marks corrupt group bitmaps.
- `ext4_has_free_clusters()` and `ext4_claim_free_clusters()` enforce reserved-block, dirty-cluster, root-reserved, and allocation-reserved accounting.
- `ext4_should_retry_alloc()` decides whether ENOSPC paths should wait for journal commits or discard work and retry.
- `ext4_new_meta_blocks()` wraps multiblock allocation for metadata and accounts quota for delayed-allocation reservations.
- `ext4_bg_has_super()`, `ext4_bg_num_gdb()`, and `ext4_num_base_meta_blocks()` compute backup super/GDT placement.

## Integration Points
Uses ext4 group descriptors, block/inode bitmap checksum helpers, mballoc, JBD2, quota accounting, mount options, flex_bg/meta_bg/sparse_super features, KUnit static stubs, and tracepoints.

## Risks and Edge Cases
Bitmap validation is central corruption defense; failures mark group bitmaps corrupt and can remount/error the filesystem. Bigalloc cluster math, flex_bg layouts, meta_bg layouts, and last-group sizing make off-by-one errors high risk. Allocation retry is intentionally bounded to avoid infinite ENOSPC loops.
