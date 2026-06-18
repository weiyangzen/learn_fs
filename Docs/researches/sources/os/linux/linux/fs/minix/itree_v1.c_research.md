# File Research: sources/os/linux/linux/fs/minix/itree_v1.c

## Purpose
Specializes `itree_common.c` for Minix V1, whose on-disk block pointers are 16-bit values and whose tree supports direct, single-indirect, and double-indirect addressing.

## Main Responsibilities
- Define V1 indirect-tree shape and pointer type.
- Convert logical block numbers into V1 pointer offsets.
- Expose V1 block mapping, truncation, and block-count helpers to `inode.c`.

## Key Constants and Types
- `DEPTH = 3`: direct, single indirect, double indirect.
- `DIRECT = 7`: seven direct zone pointers.
- `block_t = u16`: V1 stores 16-bit block/zone pointers.
- Single-indirect fanout is fixed at 512 entries because V1 uses 1 KiB blocks with 16-bit entries.

## Key Functions
- `block_to_cpu()` and `cpu_to_block()` are identity conversions for host-order `u16`.
- `i_data()` returns the V1 `i1_data` pointer array from `minix_inode_info`.
- `block_to_path()` maps a logical block to offsets:
  - blocks `0..6` use direct pointers;
  - next `512` blocks use pointer `7`;
  - remaining supported blocks use pointer `8` for double indirect.
- `V1_minix_get_block()` delegates to generic `get_block()`.
- `V1_minix_truncate()` delegates to generic `truncate()`.
- `V1_minix_blocks()` delegates to generic `nblocks()`.

## Important Behaviors and Edge Cases
- Negative logical blocks are rejected and logged.
- Blocks whose byte offset would exceed `s_maxbytes` are rejected by returning depth zero.
- V1 only supports double indirect addressing; V1 maximum file-size validation is also enforced in `inode.c`.

## Dependencies
- Includes `itree_common.c` after defining all required macros/types.
- Uses `minix_i()` and V1 inode data layout from `minix.h`.

## Research Notes
The file is intentionally small because all tree mechanics are shared. Its main semantic contribution is the V1 path calculation and the 16-bit pointer format.
