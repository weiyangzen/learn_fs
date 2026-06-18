# File Research: sources/os/linux/linux/fs/omfs/bitmap.c

OMFS free-space bitmap management. This file keeps the in-memory allocation bitmap synchronized with the on-disk bitmap when one exists.

Main responsibilities:
- `omfs_count_free()` counts free bits across all in-memory bitmap pages.
- `omfs_allocate_block()` tries to allocate exactly one filesystem block/cluster number.
- `omfs_allocate_range()` finds and marks a contiguous run, used for inode mirror blocks and file cluster allocation.
- `omfs_clear_range()` clears a contiguous allocation run during truncate or inode eviction.
- Internal helpers count free runs across bitmap-buffer boundaries and set/clear runs in both memory and disk bitmap buffers.

Implementation details:
- Allocation state is protected by `sbi->s_bitmap_lock`.
- The bitmap is held as `unsigned long **s_imap`, one allocation per filesystem block of bitmap data.
- On-disk bitmap blocks are addressed from `s_bitmap_ino` through `clus_to_blk()`.
- `set_run()` handles runs that cross bitmap blocks by dirtying and releasing one bitmap buffer before loading the next.
- `omfs_allocate_range()` returns the selected starting block and the full available run length up to `max_request`, provided it meets `min_request`.

Important behavior:
- `omfs_allocate_block()` returns boolean success rather than a negative errno.
- `omfs_allocate_range()` returns `-ENOSPC` when no run satisfies the request.
- `omfs_clear_range()` treats an out-of-range starting map as a no-op.
- If a disk bitmap read fails during allocation after the in-memory bit was set, the function exits without rolling back that bit.
