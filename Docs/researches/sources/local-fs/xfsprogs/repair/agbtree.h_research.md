# File Research: sources/local-fs/xfsprogs/repair/agbtree.h

## Purpose
Declares shared repair structures and functions for rebuilding per-AG btrees.

## Key Elements
Defines `struct bt_rebuild`, containing a `bulkload` fake-root/reservation context, `xfs_btree_bload` geometry, staged cursor, and a union of tree-specific cursors/state for free-space, inode, rmap, and refcount rebuilds.

Declares initialization and build functions for free-space btrees, inode btrees, rmapbt, and refcountbt, plus `finish_rebuild` and `estimate_agbtree_blocks`.

## Dependencies
Requires repair bulkload structures, xfs btree cursor types, slab cursors, in-core extent and inode tree nodes, and libfrog bitmap.

## Behavior/Risks
The union makes the rebuild context compact but tree-specific fields must only be used by the matching init/build path. Callers are responsible for sequencing init, bulk-load build, header update, and finish/cleanup correctly.
