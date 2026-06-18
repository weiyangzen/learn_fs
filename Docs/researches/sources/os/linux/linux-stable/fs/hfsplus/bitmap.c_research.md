# File Research: sources/os/linux/linux-stable/fs/hfsplus/bitmap.c

## Scope

Manages allocation bitmap bits for HFS+ allocation blocks.

## APIs And Behavior

- `hfsplus_block_allocate()` scans the allocation file bitmap from a requested offset, finds a free bit, sets up to `*max` contiguous free bits, updates `*max` to the allocated length, decrements `free_blocks`, marks bitmap pages dirty, and marks the MDB dirty.
- `hfsplus_block_free()` clears a range of allocation bits, validates the range against `total_blocks`, increments `free_blocks`, marks pages/MDB dirty, and reports page read failures as `-EIO`.

## State And Dependencies

Uses `HFSPLUS_SB(sb)->alloc_file`, `alloc_mutex`, `total_blocks`, `free_blocks`, and page-cache reads of the allocation file. Bitmap bits are big-endian u32 words with high bit representing the first block in a word.

## Risks And Invariants

The allocator may allocate fewer blocks than requested and reports that through `*max`. It uses page-cache pages from the allocation file and marks them dirty, so allocation metadata writeback depends on normal inode writeback plus MDB dirtying. Freeing does not verify bits were previously set; it clears the requested range.
