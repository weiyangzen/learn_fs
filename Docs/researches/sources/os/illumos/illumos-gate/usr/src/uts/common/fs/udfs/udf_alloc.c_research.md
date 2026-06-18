# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_alloc.c

UDF allocation and inode lifecycle support: bitmap/space-table block allocation, block freeing, inode allocation/freeing, truncate-space entry point, and metadata allocation cache.

Key responsibilities:
- Implements `ud_alloc_space()` to allocate blocks from a requested partition, optionally from the metadata cache, dispatching to bitmap or space-table allocation and updating free-block counters.
- Implements bitmap allocation in `ud_alloc_space_bmap()`, including proximity allocation, last-allocation scanning, cluster alignment while not fragmented, fallback to fragmented scanning, less-is-ok partial allocation, bitmap marking, and delayed writes.
- Implements `ud_check_free_and_mark_used()`, `ud_check_free()`, `ud_mark_used()`, and `ud_mark_free()` for bitmap manipulation.
- Implements space-table allocation in `ud_alloc_space_stbl()` for short and long allocation descriptors, using exact fit, first larger fit, or largest partial extent when `less_is_ok` is set.
- Implements `ud_free_space()` dispatching to bitmap or space-table free paths and marking the filesystem bad if free fails.
- Implements bitmap freeing in `ud_free_space_bmap()`, choosing freed-space bitmap if present or unallocated bitmap otherwise, marking blocks free, and updating free counters only when freeing directly to unallocated space.
- Implements space-table freeing in `ud_free_space_stbl()`, merging with adjacent short/long descriptor extents where possible or appending a new descriptor if space remains.
- Implements `ud_ialloc()` to allocate a file-entry block, initialize UDF file entry fields, permissions, uid/gid, times, implementation id, unique id, device extended attributes, ICB tag file type/flags, write the tag, update file/dir counters, and instantiate an inode via `ud_iget()`.
- Implements `ud_ifree()` to trash the on-disk file entry, free its ICB block, and decrement file/dir counters.
- Implements `ud_freesp()` for `F_FREESP`-style truncation to EOF, including mandatory lock checks and ordered inode locking before `ud_itrunc()`.
- Implements metadata block cache helpers `ud_alloc_from_cache()` and `ud_release_cache()` using cluster allocation and per-partition `udp_cache`.

Dependencies:
- Uses UDF volume/inode structures from `sys/fs/udf_volume.h` and `sys/fs/udf_inode.h`.
- Uses endian conversion macros such as `SWAP_16`, `SWAP_32`, and `SWAP_64`.
- Uses UDF helpers including `ud_bread`, `ud_xlate_to_daddr`, `ud_make_tag`, `ud_update_regid`, `ud_make_dev_spec_ear`, `ud_utime2dtime`, `ud_iget`, and `ud_itrunc`.
- Uses vnode/file-lock policy helpers for truncation and creation permission behavior.

Concurrency and locking:
- Filesystem-wide counters and allocation-cache state are protected by `udf_vfsp->udf_lock`.
- Bitmap buffers are modified then written with `bdwrite()`, while inode blocks use `BWRITE`/`BWRITE2`.
- `ud_freesp()` follows inode lock ordering by dropping `i_contents`, taking `i_rwlock` writer, then `i_contents` writer before truncation.
- `ud_alloc_from_cache()` releases `udf_lock` before recursively calling `ud_alloc_space()` to refill the cache.

Notable risks:
- Bitmap routines account for `HDR_BLKS` offset, so caller-visible partition block numbers differ from bitmap bit positions.
- Space-table descriptor compression loops copy one element beyond the logical last descriptor while removing an entry; this is longstanding C-style table compaction and relies on buffer slack.
- `ud_alloc_space_stbl()` declares `error` without initializing it before some success paths, but success paths jump to `end` where `if (!error)` is evaluated; this is a suspicious correctness risk in the source as read.
- `ud_release_cache()` frees cached blocks as a contiguous range starting at `udp_cache[0]`; this assumes the cache contents correspond to a contiguous cluster in ascending order.
- `ud_freesp()` explicitly notes a bug: unused bytes in the last retained block are not cleared, so a resulting hole may not read as zeroes.
