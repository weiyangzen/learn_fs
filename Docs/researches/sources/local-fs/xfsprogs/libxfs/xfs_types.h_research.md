# File Research: sources/local-fs/xfsprogs/libxfs/xfs_types.h

This header defines core XFS scalar types, null sentinels, size limits, fork identifiers, name and extent records, refcount/rmap in-core records, group/free-counter enums, and verifier prototypes.

The type aliases distinguish allocation-group blocks, realtime-group blocks, extent lengths, realtime extent lengths, AG numbers, rtgroup numbers, filesystem blocks, raw filesystem blocks, realtime blocks, file offsets, file block counts, realtime extent numbers, and realtime bitmap lengths. The separate `xfs_rgblock_t` and `xfs_rgnumber_t` types are the important realtime-group additions.

Null sentinels are provided for each block/offset/group/inode domain, including `NULLRGBLOCK` and `NULLRGNUMBER`. Block and sector size constants define legal filesystem geometry. Fork identifiers include data, attr, COW, and a staging fork used for fake/staged btree roots.

`struct xfs_bmbt_irec`, `struct xfs_refcount_irec`, and `struct xfs_rmap_irec` are in-core extent/refcount/rmap records. Refcount domains distinguish shared and COW staging records. Rmap flags distinguish attr fork, bmbt block, and unwritten state, with separate key and record flag masks.

`enum xfs_ag_resv_type` identifies AG block reservation classes, including metadata and metafile reservations. `enum xbtree_recpacking` describes btree keyspace occupancy. `enum xfs_group_type` unifies allocation groups and realtime groups for generic group helpers. `enum xfs_free_counter` defines free data blocks, free realtime extents, and zoned realtime extents immediately available to writers.

The verifier prototypes correspond to `xfs_types.c` and provide validation for data blocks/extents, inodes, directory inodes, realtime blocks/extents, inode counts, directory/attribute block offsets, and file offset ranges.
