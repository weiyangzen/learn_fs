# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_tables.c

## Purpose
Allocates block bitmaps, inode bitmaps, and inode tables for each block group during filesystem creation.

## Main Elements
- `flexbg_offset()`: chooses a free start block for metadata across flex_bg groups, preferring contiguous placement and falling back to smaller searches.
- `ext2fs_allocate_group_table()`: allocates missing block bitmap, inode bitmap, and inode table locations for one group, with special handling for stride and flex_bg layouts.
- `ext2fs_allocate_tables()`: iterates all groups, reports progress, and allocates each group’s tables.

## Dependencies And Integration
Uses allocation search from `alloc.c`, bitmap marking, group descriptor setters, free-block counter updates, group descriptor checksums, and progress callbacks. Used by mke2fs/new filesystem initialization.

## Risk Notes
Flex_bg accounting updates may charge metadata blocks to groups different from the logical group being initialized. The code has FIXME notes about backup group descriptor overlap when flex_bg allocations grow into backup descriptor regions.
