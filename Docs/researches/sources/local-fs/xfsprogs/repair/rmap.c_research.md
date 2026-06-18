# File Research: sources/local-fs/xfsprogs/repair/rmap.c

Implements xfs_repair reverse-mapping and refcount reconstruction support. It owns per-AG and per-realtime-group in-memory rmap collection, verification of existing rmap/refcount btrees, reflink flag reconciliation, and size estimation for phase-5 rebuilds.

Key structures:
- `struct xfs_ag_rmap`: per AG/rtgroup anchor for an in-memory `xfbtree`, xfile buffer target, AG-btree rmap slab, refcount item slab, and AGFL count bookkeeping.
- Global arrays `ag_rmaps` and `rg_rmaps` hold per-AG and per-rtgroup state.
- `rmapbt_suspect` and internal `refcbt_suspect` suppress verification and force rebuild behavior after scanner-detected corruption.

Core flow:
- `rmaps_init` allocates per-AG and per-rtgroup tracking when rmap/refcount work is needed.
- `rmap_add_rec`, `rmap_add_bmbt_rec`, `rmap_add_fixed_ag_rec`, and `rmap_add_fixed_rtgroup_rec` collect observed file, bmbt, fixed metadata, inode chunk, log, and rt superblock ownership.
- `compute_refcounts` walks sorted rmap observations with an `rcbag` stack to emit shared refcount records wherever overlap depth changes.
- `rmaps_verify_btree` and `rtrmaps_verify_btree` compare observed rmaps with existing ondisk AG or rtgroup rmap btrees.
- `check_refcounts` and `check_rtrefcounts` compare computed refcount slabs with existing refcount btrees.
- `fix_inode_reflink_flags` updates inode reflink flags based on observed shared extents.
- `rmap_commit_agbtree_mappings` finishes inserting AG btree and AGFL ownership records into the rebuilt rmapbt after AGF/AGFL reconstruction.
- Estimators compute expected rmap/refcount btree block counts for AG and realtime trees.

Important behavior:
- File data rmaps, bmbt blocks, metadata owners, attr fork flags, unwritten flags, and realtime mappings are normalized into `xfs_rmap_irec`.
- Only written data fork extents from regular inodes are considered shareable for refcount generation.
- Reflink flag correction is deliberately quiet unless verbose, because clearing unnecessary reflink flags is an optimization.
- AGFL handling avoids double-recording `OWN_AG` blocks already represented by rebuilt AG btree mappings.
- Realtime rmap/refcount validation checks metadata btree inode format, metatype, and forbidden attr forks.

Dependencies:
- Uses `slab.c` for refcount and delayed AG btree records.
- Uses libxfs in-memory btrees, rmap/refcount helpers, bitmap helpers, `rcbag`, `rt.h`, and inode in-core repair state.
