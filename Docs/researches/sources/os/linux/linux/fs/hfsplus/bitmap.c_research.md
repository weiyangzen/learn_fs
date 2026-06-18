# File Research: sources/os/linux/linux/fs/hfsplus/bitmap.c

Purpose: Manages HFS+ allocation-file bitmap bits for block allocation and freeing.

Key functions:
- `hfsplus_block_allocate()` scans allocation bitmap pages from a goal offset, sets a contiguous run up to caller-supplied maximum, decreases `free_blocks`, and marks MDB dirty.
- `hfsplus_block_free()` clears a range of bits, increases `free_blocks`, and marks MDB dirty.

Dependencies and integration:
- Uses `HFSPLUS_SB(sb)->alloc_file->i_mapping` for bitmap pages.
- Called by extent growth/truncation/free paths in `extents.c`.
- Protected by `sbi->alloc_mutex`.

Risk notes:
- Allocation wraps are handled by callers, not inside this function.
- Freeing trusts the requested range after bounds check; it clears bits without verifying they were previously allocated.
