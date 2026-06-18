# File Research: sources/local-fs/xfsprogs/repair/rmap.h

Public interface for repair-time rmap/refcount collection, verification, and rebuild support.

Exports:
- Global state: `collect_rmaps`, `rmapbt_suspect`.
- Lifecycle: `rmap_needs_work`, `rmaps_init`, `rmaps_free`.
- Observation collection: `rmap_add_rec`, `rmap_add_bmbt_rec`, `rmap_add_fixed_ag_rec`, `rmap_add_fixed_rtgroup_rec`, `rmap_add_agbtree_mapping`, `rmap_commit_agbtree_mappings`.
- In-memory cursor access: `rmap_init_mem_cursor`, `rmap_get_mem_rec`.
- Verification and avoidance: `rmaps_verify_btree`, `rtrmaps_verify_btree`, `rmap_avoid_check`, `refcount_avoid_check`.
- Refcount generation/access: `compute_refcounts`, `refcount_record_count`, `init_refcount_cursor`, `check_refcounts`, `check_rtrefcounts`.
- Reflink flag repair: `record_inode_reflink_flag`, `fix_inode_reflink_flags`.
- Rebuild estimation/population: AG rmap/refcount and realtime rmap/refcount block estimators plus rtgroup btree population entry points.

This header is the bridge between phase scanners, inode repair, AG btree rebuild code, and realtime metadata rebuilders.
