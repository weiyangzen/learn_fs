# File Research: sources/local-fs/xfsprogs/repair/agbtree.c

## Purpose
Rebuilds per-allocation-group btrees during xfs_repair phase work using libxfs bulk-loading infrastructure.

## Key Elements
`bt_rebuild` contexts are initialized by `init_rebuild`, which sets up fake-root bulkload state and geometry slack. `reserve_agblocks` consumes smallest free extents from repair’s in-memory bno/bcnt trees, reserves them for rebuilt btrees, adds rmap records for the reservations, and updates free-space trees.

Free-space btree rebuild initializes bnobt and cntbt cursors, iteratively computes geometry because reservations change free-space records, leaves enough extra blocks for AGFL setup, and bulk-loads records from in-memory extent trees.

Inode btree rebuild computes inode/free-inode totals, handles sparse inode holemask conversion, builds inobt and optionally finobt, and tracks first agino/count/freecount in rebuild state.

Rmap and refcount rebuilds are feature-gated by `xfs_has_rmapbt` and `xfs_has_reflink`, respectively. They feed records from repair rmap cursors or refcount slab cursors into libxfs bulk loaders.

`finish_rebuild` marks unused reserved blocks as lost blocks before committing reservations. `estimate_agbtree_blocks` estimates allocbt, inobt/finobt, rmapbt, and refcountbt block needs.

## Dependencies
Depends on libxfs btree/bulkload APIs, repair in-core extent/inode/rmap/refcount structures, `bulkload.h`, `incore.h`, `rmap.h`, `slab.h`, and libfrog bitmap utilities.

## Behavior/Risks
This code mutates repair’s in-memory free-space records while reserving blocks for new metadata, so ordering matters. It intentionally does not commit btree cursors when AGF/AGI headers have not yet been written. Reservation shortfalls are fatal because repaired metadata cannot be safely written without space for the rebuilt trees and AGFL.
