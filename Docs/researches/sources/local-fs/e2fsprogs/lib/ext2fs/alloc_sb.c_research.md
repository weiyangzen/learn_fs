# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_sb.c

## Purpose
Reserves superblock and group descriptor blocks for newly initialized filesystems, primarily for mke2fs.

## Main Elements
- `ext2fs_reserve_super_and_bgd()`: computes superblock/old descriptor/new descriptor locations for a group, marks those blocks in a bitmap, handles 1K blocksize bigalloc block zero, and returns an estimated free block count.
- `ext2fs_reserve_super_and_bgd2()`: calls the first routine then counts used blocks in the group to return descriptor/super usage.

## Dependencies And Integration
Uses `ext2fs_super_and_bgd_loc2()`, group descriptor sizing, feature checks for `meta_bg`, bitmap marking, and used-block counting. It is part of filesystem initialization/allocation table setup.

## Risk Notes
The comment warns the original return value assumes inode tables and bitmaps live in the group, which is not necessarily true with `flex_bg`; callers must not overinterpret the free-block estimate.
