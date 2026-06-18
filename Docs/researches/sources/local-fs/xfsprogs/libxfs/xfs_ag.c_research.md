# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag.c

## Role

`xfs_ag.c` implements allocation-group infrastructure for userspace libxfs: per-AG initialization and teardown, incore counter rebuilding, AG/inode geometry helpers, new AG header construction for growfs, tail-AG shrink/extend operations, growfs delta computation, and AG geometry reporting.

## Major Responsibilities

- Rebuild incore superblock inode/free-block counters by reading every AGF/AGI.
- Allocate and insert `struct xfs_perag` objects into the generic xfs group table.
- Free per-AG resources over a specified AG range.
- Calculate AG block counts, including the shorter final AG.
- Calculate valid AG inode-number ranges based on AGFL location and inode cluster alignment.
- Update the previous last AG size after growfs recovery.
- Initialize secondary superblocks, AGF, AGFL, AGI, and root btree blocks for new AGs.
- Shrink the final AG after validating inode and free-space constraints.
- Compute growfs block delta and resulting AG count.
- Extend the final AG and free the newly added space.
- Return AG geometry and health information.

## Per-AG Initialization

`xfs_initialize_perag` allocates per-AG objects from the old AG count to the new AG count. `xfs_perag_alloc` allocates the structure, initializes its buffer cache, computes block count and minimum group block number, precalculates valid inode range, and inserts it through `xfs_group_insert`. On failure, new perags are unwound with `xfs_free_perag_range`.

`xfs_initialize_perag_data` reads each AGF and AGI to populate perag counters, sums free inodes, total inodes, free blocks, freelist blocks, and btree blocks, validates the totals against the superblock, updates incore counters under `m_sb_lock`, and reinitializes percpu counters.

## New AG Header Initialization

`xfs_ag_init_headers` prepares uncached buffers for all headers and root blocks required by a new AG. It initializes:

- secondary superblock, marked `sb_inprogress`
- AGF with bno/cnt roots, levels, freelist state, free blocks, rmap/refcount roots when enabled
- AGFL with CRC fields and `NULLAGBLOCK` buckets
- AGI with inobt/finobt roots, levels, counts, UUID, unlinked buckets, and inobtcount fields
- bnobt/cntbt roots with initial free-space records
- inobt/finobt roots
- rmapbt root records for static metadata, AG btrees, inode btrees, refcountbt, and internal log when present
- refcountbt root when reflink is enabled

Prepared buffers are queued to the caller's delayed-write list.

## Shrink And Extend

`xfs_ag_shrink_space` only applies to the last AG. It reads AGI/AGF, checks matching lengths and nonzero remaining length, verifies the new end will not overlap inode clusters, frees per-AG reservations, allocates the to-be-removed tail extent exactly out of free-space btrees, tries to reinitialize reservations against the shorter AG, updates AGI/AGF lengths and perag geometry, and logs header length fields. Error paths roll transactions where needed to preserve AGFL fixes and restore reservations.

`xfs_ag_extend_space` also targets the last AG. It increases AGI and AGF lengths, logs both, removes the new space from rmap as skipped-update space, frees the extent into normal free space accounting, and updates perag block count and inode range.

## Geometry Reporting

`xfs_ag_get_geometry` locks AGI and AGF via read helpers, fills `struct xfs_ag_geometry` with AG number, inode counts, length, and free blocks. Reported free blocks include free, freelist, and btree blocks minus needed per-AG reservations, then health state is attached through `xfs_ag_geom_health`.

## Notable Assumptions

- AG shrink/extend is restricted to the current last AG.
- New AG headers are written through uncached buffers because they can be beyond current valid filesystem address space.
- The growfs code relies on `sb_inprogress` in secondary superblocks to detect incomplete activation.
- Rmap initialization during grow does not account for internal log space except where explicitly present in an AG.
