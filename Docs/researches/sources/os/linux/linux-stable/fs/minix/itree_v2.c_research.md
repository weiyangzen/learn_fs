# File Research: sources/os/linux/linux-stable/fs/minix/itree_v2.c

## Purpose

Specializes `itree_common.c` for MINIX V2/V3 block pointers.

## Main Entry Points

- `V2_minix_get_block()`: maps or allocates a V2/V3 logical block.
- `V2_minix_truncate()`: truncates V2/V3 block trees.
- `V2_minix_blocks()`: computes V2/V3 block usage for stat output.
- `block_to_path()`: converts logical blocks into direct/single/double/triple-indirect offsets.

## Control Flow And State

V2/V3 use seven direct pointers plus single, double, and triple indirect pointers with 32-bit block numbers. The indirect fanout is derived from the mounted block size with `INDIRCOUNT(sb)`. `block_to_path()` rejects negative and beyond-maximum offsets, then fills offsets for the correct tree depth.

## Dependencies

Includes `minix.h`, buffer-head support, and `itree_common.c`. Uses `minix_i(inode)->u.i2_data` and host-order `u32` block numbers.

## Risks

The triple-indirect path uses larger arithmetic and block-size-dependent fanout, so maximum-size validation and offset calculations must remain consistent with superblock block size. As with V1, the shared allocator assumes invalid logical blocks never reach it.
