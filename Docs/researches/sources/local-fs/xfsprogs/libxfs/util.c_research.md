# File Research: sources/local-fs/xfsprogs/libxfs/util.c

## Role

`util.c` collects userspace libxfs support routines that do not fit neatly into the buffer or transaction layer: log reservation sizing, reproducible timestamps, simple incore superblock modification, file-space allocation, verifier/corruption diagnostics, userspace LSN tracking, health stubs, extent zeroing, and mapped file writes.

## Major Responsibilities

- Calculate worst-case log unit reservations with `xfs_log_calc_unit_res`.
- Provide `current_time`, honoring `SOURCE_DATE_EPOCH` through `current_fixed_time`.
- Modify incore free-block counters with `libxfs_mod_incore_sb`.
- Allocate file space with `libxfs_alloc_file_space`.
- Emit verifier diagnostics for buffers and inodes.
- Track the largest metadata LSN seen by userspace repair in `xfs_log_check_lsn`.
- Initialize generic log items with `xfs_log_item_init`.
- Choose data vs realtime buftarg for inode extents and zero extents via `libxfs_zero_extent`.
- Provide minimal filesystem/group/inode sickness hooks for userspace.
- Write data through mapped filesystem extents with `libxfs_file_write`.

## Allocation Flow

`libxfs_alloc_file_space` validates positive length, converts byte range to filesystem blocks, honors realtime inodes and extent-size hints, and loops until the requested range is allocated. Each iteration computes bounded data/realtime reservations, allocates and joins an inode transaction, extends extent-count capacity, calls `xfs_bmapi_write`, sets the preallocation flag, logs the inode core, commits, and unlocks the inode. If `xfs_bmapi_write` returns no mappings for a delalloc conversion attempt, the loop retries the same offset.

## Diagnostics And LSN Tracking

`xfs_verifier_error`, `xfs_inode_verifier_error`, and `xfs_buf_corruption_error` emit concise metadata corruption/CRC messages without kernel stack dumping. `xfs_log_check_lsn` always returns true because userspace lacks an active log current-LSN source, but it records the largest non-null LSN seen under a pthread mutex for repair validation.

## File Write Helper

`libxfs_file_write` maps file offsets to data-device extents in chunks up to 1 MiB, rejects holes and unwritten extents, gets the underlying data-device buffer, copies caller data into the correct block offset, zero-fills partial leading/trailing regions within the buffer, marks it dirty, and releases it.

## Notable Assumptions

- Only `XFS_TRANS_SB_FDBLOCKS` is supported by `libxfs_mod_incore_sb`.
- Health marking is mostly stubbed in userspace; `xfs_fs_mark_healthy` updates fs-level sick/checked bits, while most mark-sick helpers are empty.
- `xfs_log_check_lsn` validates nothing against an active log and is intentionally permissive.
- `libxfs_file_write` requires fully mapped, written extents and treats holes/unwritten extents as caller errors.
