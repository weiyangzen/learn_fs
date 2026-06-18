# File Research: sources/os/linux/linux/fs/nilfs2/sufile.c

`sufile.c` implements the NILFS segment usage metadata file. It tracks clean, dirty, active, and erroneous segments; allocates new segments; frees/scraps/cancels segments; exposes usage stats to ioctl callers; supports resize; and issues discard/TRIM over clean segment ranges.

`struct nilfs_sufile_info` embeds `nilfs_mdt_info` and adds cached clean-segment count plus an allocatable segment-number range. Helpers map segment numbers to metadata block offsets and entry offsets using metadata entry sizing from `mdt.h`.

Update helpers serialize changes under `NILFS_MDT(sufile)->mi_sem`. `nilfs_sufile_update()` and `nilfs_sufile_updatev()` fetch the header and relevant usage blocks, then invoke primitive operations such as scrap, free, cancel-free, or set-error. Header clean/dirty counters and the cached `ncleansegs` value are kept in sync.

`nilfs_sufile_alloc()` scans from the last allocation within the configured range, wraps through the range and fallback regions, finds a clean segment, marks it dirty, decrements clean count, increments dirty count, stores `sh_last_alloc`, marks metadata dirty, and returns the selected segment. `nilfs_sufile_mark_dirty()` protects active or allocated segments and rejects erroneous active segments.

`nilfs_sufile_resize()` grows or shrinks the segment array. Shrinking verifies the truncated range contains only clean/error segments and no active segments, deletes full usage blocks as holes, updates counters, and adjusts allocation bounds before publishing the new segment count.

`nilfs_sufile_get_suinfo()` and `nilfs_sufile_set_suinfo()` implement bulk user-visible segment-usage inspection/update, masking the active flag on disk because active is a runtime projection. `nilfs_sufile_trim_fs()` coalesces clean contiguous segment ranges and calls `blkdev_issue_discard()`.
