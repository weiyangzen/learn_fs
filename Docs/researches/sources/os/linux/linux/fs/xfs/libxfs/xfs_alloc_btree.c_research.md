# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.c

Implements XFS free-space btree operations for the by-block-number btree and by-block-count btree.

Key behavior:
- Maintains a cursor slab cache for allocation btree cursors.
- Provides cursor duplication for bnobt and cntbt.
- Updates AGF root pointers and level counters when btree roots change, synchronizing perag cached levels.
- Allocates new btree blocks from the AGFL, marks them busy-reused, and increments global allocbt block count.
- Frees btree blocks back to the AGFL, marks them busy with discard skipped, and decrements global allocbt block count.
- Provides min/max record counts from mount geometry.
- Initializes keys, high keys, records, and root pointers from records/cursors.
- Implements bnobt comparisons by start block.
- Implements cntbt comparisons by block count, then start block.
- Verifies alloc btree blocks:
  - magic and CRC headers.
  - perag-aware tree level limits when AGF is initialized.
  - repair-height allowances during online repair.
  - mount maximum levels when perag is unavailable or uninitialized.
  - generic AG btree block structure.
- Defines buffer ops for bnobt and cntbt.
- Enforces key/record ordering:
  - bnobt records must be non-overlapping and start-block ordered.
  - cntbt records are ordered by length then start block.
- Defines `xfs_btree_ops` for bnobt and cntbt, including sick masks, stat offsets, buffer ops, key comparisons, allocation/free block hooks, and ordering checks.
- Initializes bnobt/cntbt cursors with held AG group references and AGF-derived tree levels.
- Commits staged btree roots for online repair/rebuild flows.
- Computes alloc btree records per block, maximum on-disk levels, and btree size estimates.
- Initializes and destroys the allocation btree cursor cache.

Important interactions:
- `xfs_alloc.c` uses these btree ops to search, allocate, free, merge, and query free-space extents.
- AGF fields are the persistent roots and height counters for both free-space btrees.
- Online repair can stage replacement free-space btrees before committing new roots.
