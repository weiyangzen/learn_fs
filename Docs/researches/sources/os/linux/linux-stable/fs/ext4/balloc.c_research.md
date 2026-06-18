# File Research: sources/os/linux/linux-stable/fs/ext4/balloc.c

## Purpose

Implements ext4 block group allocation support, bitmap loading/validation, free-space accounting, metadata block allocation helpers, backup superblock/GDT placement calculations, and allocation goal selection.

## Main Responsibilities

- Maps filesystem block numbers to block groups and bitmap offsets.
- Initializes uninitialized block bitmaps.
- Computes per-group metadata overhead and free clusters.
- Loads group descriptors and group info structures.
- Reads and validates block allocation bitmaps.
- Checks and claims free cluster availability.
- Retries allocations after ENOSPC when journal/discard progress may free blocks.
- Allocates metadata blocks through ext4 multiblock allocator.
- Counts free clusters across block groups.
- Computes backup superblock/group descriptor placement.
- Chooses inode-local allocation goal blocks.

## Key Operations

- `ext4_get_group_number()` and `ext4_get_group_no_and_offset()` convert block addresses to group/offset values, accounting for cluster size.
- `ext4_num_overhead_clusters()` counts base metadata, inode table clusters, and bitmap clusters while avoiding double counting.
- `ext4_init_block_bitmap()` zeros an uninitialized bitmap, marks metadata clusters used, marks bitmap padding, and verifies group descriptor checksum.
- `ext4_free_clusters_after_init()` estimates free clusters for uninitialized block bitmaps.
- `ext4_get_group_desc()` returns a group descriptor from the RCU-managed descriptor buffer array and validates group bounds.
- `ext4_valid_block_bitmap()` checks that block bitmap, inode bitmap, and inode table bits are set in a loaded bitmap.
- `ext4_validate_block_bitmap()` verifies checksum, structural bitmap correctness, and end padding, then marks the buffer verified.
- `ext4_read_block_bitmap_nowait()` gets/loads a bitmap buffer, initializes uninitialized bitmaps when permitted, submits async metadata reads, and validates already-present bitmaps.
- `ext4_wait_block_bitmap()` waits for async bitmap I/O and validates the loaded bitmap.
- `ext4_read_block_bitmap()` wraps nowait plus wait.
- `ext4_has_free_clusters()` accounts for free clusters, dirty clusters, reserved blocks, root-reserved blocks, and privileged allocation flags.
- `ext4_claim_free_clusters()` reserves dirty clusters if space is available.
- `ext4_should_retry_alloc()` retries ENOSPC up to three times when journal commits or discard work might release blocks.
- `ext4_new_meta_blocks()` allocates metadata blocks through `ext4_mb_new_blocks()`.
- `ext4_count_free_clusters()` sums free clusters from group descriptors, skipping corrupt bitmap groups.
- `ext4_bg_has_super()`, `ext4_bg_num_gdb()`, and `ext4_num_base_meta_blocks()` calculate backup superblock and descriptor metadata placement for sparse/meta_bg variants.
- `ext4_inode_to_goal_block()` chooses an allocation goal based on inode group, flex_bg layout, file type, delayed allocation, and process-derived color.

## Dependencies

- Includes ext4 core headers, journaling header, mballoc header, trace events, and KUnit static stubs.
- Depends on metadata checksum helpers, group locking, bitmap helpers, ext4 error reporting, buffer heads, JBD2, quota accounting, and multiblock allocator APIs.

## Research Notes

This file is defensive around allocator metadata. Bitmap data is not trusted until descriptor checksums, bitmap checksums, required metadata bits, and padding bits validate. It also contains important policy around reserved clusters and privileged allocation access.
