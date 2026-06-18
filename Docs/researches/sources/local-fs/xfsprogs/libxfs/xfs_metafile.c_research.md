# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metafile.c

## Role

This file implements metadata inode flag management and global reservation accounting for metadata btree files. It currently focuses on metadata files under the metadir feature, especially realtime rmap and realtime refcount btree metadata.

## Metadata Inode Flags

`xfs_metafile_type_str` maps `enum xfs_metafile_type` values to strings.

`xfs_metafile_set_iflag` turns an inode into a metadata inode by clearing permissions, setting root uid/gid, adding mandatory directory or file metadata flags, clearing DAX, setting `XFS_DIFLAG2_METADATA`, storing the metatype, logging the inode core, and moving inode stats from active to metadata.

`xfs_metafile_clear_iflag` clears the metadata flag for zero-link metadata inodes, logs the inode, and adjusts stats back.

## Reservation Criticality

`xfs_metafile_resv_can_cover` tests whether available metadata reservation plus free filesystem blocks can cover a requested block count.

`xfs_metafile_resv_critical` reports critical reservation state if available space cannot cover maximum realtime btree height or 10% of target reservation, or if an error tag forces it.

## Reservation Allocation

`xfs_metafile_resv_alloc_space` charges allocated blocks first against the hidden metadata reservation, updating delayed allocation and reserved fdblocks superblock counters. If allocation exceeds the reservation, it tries to decrement normal free blocks or consume transaction block reservation. It updates used count, inode block count, and logs the inode.

`xfs_metafile_resv_free_space` decrements inode block count and used reservation, returns blocks to hidden reservation up to the target, updates reserved fdblocks, and returns any excess to normal free blocks.

## Reservation Lifecycle

`xfs_metafile_resv_init` resets existing state, walks realtime groups, sums used blocks and target reserves for realtime rmap and refcount btrees, caps reservation to one quarter of data blocks, hides unused target space from free blocks by moving it to delalloc accounting, and stores target/used/available counts.

`xfs_metafile_resv_free` releases unused hidden reservation back to free blocks.

## Dependencies

This file depends on metadir feature checks, realtime group iteration, realtime rmap/refcount btree reserve calculators, allocation args, transaction superblock accounting, inode logging, mount counters, and error tags.

## Research Notes

The reservation model intentionally hides unused metadata reserve space from free block accounting while keeping already-used metadata btree blocks accounted as used on disk. Any new metadata btree file requiring reserve space must be added to the reserve init loop.
