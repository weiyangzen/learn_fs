# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Super.c

This file initializes and prints ext2 superblock and group accounting state.

Core responsibilities:
- `ext2_print_super` dumps key superblock fields, UUID bytes, and label through debug printing.
- `ext2_initialize_sb` fills default superblock fields, computes block/group/inode layout, allocates bitmaps and group descriptors, reserves superblock/group descriptor blocks, and initializes per-group free counts.

Important behavior:
- Block size and fragment size are derived from ext2 log fields.
- First data block is 1 for 1 KiB block filesystems and 0 for larger blocks.
- Inodes per group are rounded to fill inode table blocks and then rounded down to a multiple of 8.
- If the final group is too small for metadata, the filesystem block count is reduced and layout is recomputed.
- Group descriptor and bitmap allocations happen after layout is stable.

Risk points:
- The last group can be silently trimmed if it is too small.
- Free block counts assume metadata overhead per group and sparse-super reservations but do not model newer ext features.
- Initialization fails and frees partial allocations on cleanup, so callers must not reuse stale pointers after failure.
