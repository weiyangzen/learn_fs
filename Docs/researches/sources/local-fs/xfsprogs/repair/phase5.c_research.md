# File Research: sources/local-fs/xfsprogs/repair/phase5.c

## Role

`phase5.c` implements xfs_repair phase 5: rebuilding allocation group headers and per-AG btrees from the in-core state established by earlier phases. It reconstructs free-space btrees, inode btrees, optional rmap/refcount btrees, AGF/AGFL/AGI headers, superblock counters, and realtime metadata checks.

## Core Flow

- `mk_incore_fstree()` scans the phase bitmap for each AG and converts unknown/free regions into in-core bno/bcnt extent trees.
- `phase5_func()` rebuilds one AG: estimates btree space, initializes rebuild cursors, builds free-space, inode, rmap, and refcount trees, writes AGF/AGFL/AGI, and accounts per-AG superblock counters.
- `phase5()` preserves root/realtime fixed inodes, allocates per-AG counter arrays, decides whether packed btrees are needed, processes all AGs, syncs the primary superblock, commits AG btree rmap records, reinserts lost reserved blocks, and clears `bad_ino_btree`.
- `check_rtmetadata()` dispatches zoned filesystem checks or legacy realtime bitmap/summary validation.

## Important Data

- `sb_icount_ag`, `sb_ifree_ag`, and `sb_fdblocks_ag` accumulate per-AG counter rebuild results before aggregation.
- `lost_blocks` records blocks reserved but ultimately not consumed by btree rebuilding so they can be freed back to the filesystem.
- `need_packed_btrees` is set when realtime btree metadata could consume enough free space that denser btree packing is required.

## Dependencies

This file depends heavily on repair bulkload helpers, AG btree rebuild helpers, in-core block maps, rmap/refcount reconstruction, realtime repair code, zoned metadata checks, libxfs buffer/trans APIs, and progress reporting.

## Risk Areas

- Phase 5 trusts the in-core block and inode state built by earlier phases; bad earlier classification can create bad rebuilt metadata.
- Space accounting is delicate because btree roots, AGFL blocks, lazy superblock counters, and rmap/refcount blocks are accounted differently.
- Low-free-space filesystems depend on `are_packed_btrees_needed()` estimating metadata space conservatively enough.
