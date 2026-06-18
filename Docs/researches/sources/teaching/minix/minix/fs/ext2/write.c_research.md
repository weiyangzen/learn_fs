# File Research: sources/teaching/minix/minix/fs/ext2/write.c

This file implements write-side block mapping, indirect block allocation/freeing, and new block acquisition.

Key entry points:
- `write_map(rip, position, new_wblock, op)`: inserts or frees a block mapping at a file offset, including direct, single, double, and triple indirect paths.
- `new_block(rip, position)`: allocates and maps a block for a file offset, choosing sequential allocation goals when possible.
- `zero_block(bp)`: zeros an LMFS buffer and marks it dirty.

Internal helpers:
- `wr_indir(bp, index, block)`: writes one indirect-block entry with endian conversion.
- `empty_indir(bp, sb)`: checks if an indirect block has only `NO_BLOCK` entries.

Important behavior:
- `write_map()` is the authority for maintaining `i_blocks`.
- Frees empty indirect blocks recursively after removing data blocks.
- Allocates new indirect blocks on demand and zeroes them before use.
- `new_block()` disables preallocation on non-sequential writes.

Notable risk:
- `empty_indir()` compares raw `b_ind(bp)[i]` with `NO_BLOCK` without conversion, unlike `rd_indir()`; this is harmless on asserted little-endian but inconsistent with conversion-aware code.
