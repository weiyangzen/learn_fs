# File Research: sources/os/linux/linux/fs/minix/itree_v2.c

## Purpose
Specializes `itree_common.c` for Minix V2 and V3, whose block pointers are 32-bit values and whose tree supports direct, single-indirect, double-indirect, and triple-indirect addressing.

## Main Responsibilities
- Define V2/V3 indirect-tree shape and pointer type.
- Calculate block pointer offsets according to current superblock block size.
- Expose V2/V3 block mapping, truncation, and block-count helpers to `inode.c`.

## Key Constants and Types
- `DIRECT = 7`: seven direct zone pointers.
- `DEPTH = 4`: direct, single, double, and triple indirect.
- `block_t = u32`: V2/V3 stores 32-bit block/zone pointers.
- `DIRCOUNT = 7`.
- `INDIRCOUNT(sb) = 1 << (sb->s_blocksize_bits - 2)`, the number of 32-bit entries in an indirect block.

## Key Functions
- `block_to_cpu()` and `cpu_to_block()` are identity conversions for host-order `u32`.
- `i_data()` returns the V2/V3 `i2_data` pointer array from `minix_inode_info`.
- `block_to_path()` maps a logical block through direct, single, double, or triple indirect offsets based on filesystem block size.
- `V2_minix_get_block()` delegates to generic `get_block()`.
- `V2_minix_truncate()` delegates to generic `truncate()`.
- `V2_minix_blocks()` delegates to generic `nblocks()`.

## Important Behaviors and Edge Cases
- Negative logical blocks are rejected and logged.
- Logical blocks whose byte offset exceeds `s_maxbytes` are rejected.
- Triple-indirect addressing places practical mapping limits far above the V1 limit.
- Fanout changes with superblock block size, so V3 larger blocks naturally increase indirect capacity.

## Dependencies
- Includes `itree_common.c` after V2/V3 definitions.
- Uses `minix_i()` and V2 inode data layout from `minix.h`.

## Research Notes
This wrapper covers both Minix V2 and V3 because their in-memory pointer tree logic is compatible. V3 differences are primarily superblock/block-size details handled by `inode.c`.
