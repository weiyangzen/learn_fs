# File Research: sources/os/linux/linux-stable/fs/nilfs2/sufile.c

`sufile.c` implements the NILFS segment usage metadata file. It tracks clean/dirty/error segment state, allocation ranges, live block counts, modification times, resize behavior, user-visible suinfo queries/updates, and discard trimming of clean segments.

`struct nilfs_sufile_info` embeds `nilfs_mdt_info` and adds cached clean-segment count plus allocatable segment bounds. Helpers compute the metadata block and entry offset for a segment number, account for the header block’s first-entry offset, and retrieve header or segment-usage blocks through `nilfs_mdt_get_block()`.

Update primitives serialize on `NILFS_MDT(sufile)->mi_sem`. `nilfs_sufile_update()` and `nilfs_sufile_updatev()` validate segment numbers, fetch the header and affected usage blocks, then invoke operation callbacks. Callback primitives implement cancel-free, scrap, free, and set-error semantics while keeping on-disk header counters and cached `ncleansegs` consistent.

Allocation scans from `sh_last_alloc + 1`, wraps through the configured alloc range and then the rest of the segment space as allowed, finds clean segment entries, marks them dirty, updates clean/dirty counters and last allocation, marks metadata dirty, and returns `-ENOSPC` if none are available. `nilfs_sufile_mark_dirty()` marks an existing segment dirty but refuses erroneous active segments. `nilfs_sufile_set_segment_usage()` updates live block count and optional modification time after a write.

Resize is guarded by the metadata semaphore and checks reserved-segment/free-space constraints. Shrinking calls `nilfs_sufile_truncate_range()`, which rejects dirty or active segments, clears error flags to clean when possible, deletes complete metadata blocks as holes, updates counters, and tightens allocation bounds immediately to prevent allocation into truncated space. Expansion adjusts clean segment count and global segment count.

User-facing information APIs include `nilfs_sufile_get_stat()`, `nilfs_sufile_get_suinfo()`, and `nilfs_sufile_set_suinfo()`. `get_suinfo` projects the active flag dynamically rather than reading it from disk. `set_suinfo` validates update flags and block counts, strips the virtual active flag before writing, and updates header counters based on clean/dirty transitions.

`nilfs_sufile_trim_fs()` implements fstrim over clean segments. It maps byte ranges to segment ranges, coalesces contiguous clean segments into discard extents, clamps to the requested range, honors `minlen`, and writes the discarded byte count back to `range->len`.

`nilfs_sufile_read()` loads the sufile inode, initializes metadata-file private state, validates segment usage entry size, reads the header, caches clean count, and initializes allocation range to all segments. This file is central to segment allocation by `segment.c`, recovery preparation by `recovery.c`, resize by `super.c`, and ioctls.
