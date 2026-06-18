# File Research: sources/local-fs/xfsprogs/repair/bmap_repair.c

## Purpose

`bmap_repair.c` rebuilds an inode data or attribute fork block mapping from reverse-mapping metadata. It is used when an inode fork’s extent or bmbt metadata is damaged but rmap data can still identify blocks owned by the inode.

The repair creates a fresh fork in a staged ifork, bulk-loads extents into extents or btree format, commits the staged fork to the inode, resets block counters, and leaves old bmbt blocks to be handled by later space metadata rebuild phases.

## Main Structure

`struct xrep_bmap` holds:

- A slab of new bmap records.
- A slab cursor for sorted bulk loading.
- A `bulkload` context for staging the new fork.
- An `xfs_btree_bload` descriptor.
- Repair context and target fork.
- Recomputed file block ownership counters.
- Count of old bmbt blocks found in rmap records.

## Main Flow

1. `rebuild_bmap` resets the on-disk dinode fork format/count to a zero-extent fork, starts a repair transaction, loads the inode, and calls `xrep_bmap`.
2. `xrep_bmap_check_inputs` rejects unsupported filesystems/forks/formats and skips local/dev/uuid forks.
3. `xrep_bmap_find_mappings` scans realtime rmap btrees and allocation-group rmap btrees.
4. Rmap callbacks filter records owned by the inode and fork, validate ranges/flags, and add bmap records to a slab.
5. `xrep_bmap_build_new_fork` sorts records, stages a fake fork, chooses extents or btree format, and loads the new mappings.
6. The staged bmbt is committed into the real inode fork.
7. Inode block counters are recomputed and unused reservation blocks are freed through `bulkload_commit`.

## Key Functions

- `xrep_bmap_from_rmap` converts one rmap extent into one or more bmbt records, splitting at `XFS_MAX_BMBT_EXTLEN`.
- `xrep_bmap_walk_rmap` handles data-device rmap records.
- `xrep_bmap_walk_rtrmap` handles realtime rmap records.
- `xrep_bmap_extents_load` populates an incore extent tree.
- `xrep_bmap_btree_load` computes btree geometry, reserves blocks, bulk-loads the btree, and populates incore extents.
- `xrep_bmap_reset_counters` updates `i_nblocks` from rmap-discovered blocks plus new bmbt block delta.
- `xrep_ino_ensure_extent_count` enables large extent counts if required and supported.

## Dependencies

This file depends on:

- rmapbt and realtime rmap scanning.
- slab storage and sorting.
- libxfs bmbt and generic btree bulk-loading APIs.
- `bulkload.c` for staging block reservations.
- transaction, inode, and buffer management.
- repair globals and error reporting.

## Important Invariants

- Rebuild requires rmapbt support.
- Data extents for realtime files must not appear on the data device.
- Attribute extents and bmbt blocks must not appear on realtime devices.
- Rmap flags must not combine attr/bmbt ownership with unwritten state.
- File offsets and physical extents must pass libxfs validators.
- The new fork must fit in normal or large extent-count limits.
- Transaction buffer ownership is carefully maintained across inode loading and transaction rolls.

## Repair and Risk Notes

This is a high-impact repair path: once `libxfs_bmbt_commit_staged_btree` succeeds, old fork mapping data are no longer accessible through the inode. The code relies on rmap metadata being more trustworthy than the damaged bmap. The most delicate parts are transaction/buffer handoff in `rebuild_bmap`, realtime/data-device distinction, large extent-count upgrade, and correct accounting for old versus new bmbt blocks.
