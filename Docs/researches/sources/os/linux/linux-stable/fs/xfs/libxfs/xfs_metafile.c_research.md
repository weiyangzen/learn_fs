# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.c

## Role
`xfs_metafile.c` manages metadata inode identity flags and block reservations for metadata files, particularly realtime rmap and realtime refcount btree metadata files stored in the metadata directory tree.

## Main Responsibilities
- Map metadata file type enum values to string names.
- Set and clear metadata inode flags and update active/metafile inode statistics.
- Determine whether metadata file block reservations are critically low.
- Charge allocations against metadata file reservation pools and update superblock/free block counters.
- Return freed metadata file space to the reservation or filesystem free space.
- Initialize and release mount-wide metadata file reservations.

## Important Functions
- `xfs_metafile_type_str` returns the string name for a metadata file type.
- `xfs_metafile_set_iflag` clears permissions, sets root uid/gid, applies mandatory metadata file or directory flags, clears DAX, sets `XFS_DIFLAG2_METADATA`, records metatype, logs the inode, and moves stats from active to metadata.
- `xfs_metafile_clear_iflag` clears the metadata flag on zero-link metadata inodes and reverses stats.
- `xfs_metafile_resv_critical` reports low reservation when available reserved/free space cannot cover max btree height or 10% of target reservation.
- `xfs_metafile_resv_alloc_space` consumes reservation first, then free blocks or transaction reservation, updates reservation accounting, increments `i_nblocks`, and logs the inode.
- `xfs_metafile_resv_free_space` decrements `i_nblocks`, returns blocks to reservation up to target, and sends remaining blocks to filesystem free space.
- `xfs_metafile_resv_init` computes used and target reservation for realtime rmap/refcount btrees across realtime groups, hides unused reserved space from fdblocks, and records reservation state.
- `xfs_metafile_resv_free` releases unused reservation back to filesystem free blocks.

## Data and Invariants
- Metadata files must be marked with `XFS_DIFLAG2_METADATA` and mandatory immutable/sync/noatime/nodump/nodefrag flags; metadata directories also require nosymlinks.
- Reservation accounting uses `m_metafile_resv_lock` to protect target/used/available counters.
- Reserved but unused metadata file space is hidden from normal free block accounting.
- Reservation target is bounded by current used blocks and at most one quarter of data blocks.

## Error Handling and Risks
- Reservation initialization can fail if free block reservation cannot hide the target space.
- Allocations beyond metadata reservation are expected only for rmap btree overruns and are charged carefully to either in-core or transaction counters.
- Critical-reservation checks include an error tag injection path.

## Dependencies
This file depends on realtime group iteration, realtime rmap/refcount btree reserve calculators, allocation args, transaction superblock accounting, inode logging, mount free counters, and metadata feature predicates.

## Research Notes
This file is the reservation/accounting side of metadata files. It keeps metadata btree growth from consuming all normal free space while still allowing controlled overruns for realtime metadata needs.
