# File Research: sources/os/linux/linux-stable/fs/minix/itree_v1.c

## Purpose

Specializes `itree_common.c` for MINIX V1 block pointers.

## Main Entry Points

- `V1_minix_get_block()`: maps or allocates a V1 logical block.
- `V1_minix_truncate()`: truncates V1 block trees.
- `V1_minix_blocks()`: computes V1 block usage for stat output.
- `block_to_path()`: converts a logical block into V1 direct/single/double-indirect offsets.

## Control Flow And State

V1 uses seven direct pointers, one single-indirect pointer, and one double-indirect pointer with 16-bit block numbers. `block_to_path()` rejects negative blocks and blocks beyond `s_maxbytes`, maps blocks below 7 directly, the next 512 through the single-indirect slot, and the rest through the double-indirect slot.

## Dependencies

Includes `minix.h`, buffer-head support, and the shared indirect-tree template. Uses `minix_i(inode)->u.i1_data` as the raw in-memory pointer array and assumes V1 block numbers are host-order `u16`.

## Risks

The 16-bit block pointer format and fixed 1 KiB `BLOCK_SIZE` limits make overflow and maximum-size checks important. The common code trusts `block_to_path()` to reject unrepresentable logical blocks before allocation.
