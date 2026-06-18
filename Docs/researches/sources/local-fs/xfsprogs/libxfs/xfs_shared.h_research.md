# File Research: sources/local-fs/xfsprogs/libxfs/xfs_shared.h

This shared userspace/kernel header gathers declarations and small helpers that are needed broadly across libxfs. In this group it is most important as the registry for buffer verifier ops, btree ops, transaction flags, superblock modification fields, buffer cache reference weights, and inode geometry.

The buffer ops extern list includes classic AG/inode/directory/quota/btree verifiers plus realtime-specific verifiers: realtime bitmap, realtime summary, realtime buffers, realtime superblock, realtime refcount btree, realtime rmap btree, and symlink buffers. The btree ops extern list similarly includes allocation, inode, bmap, refcount, rmap, realtime rmap, in-memory rmap variants, and realtime refcount.

Inline btree type predicates identify btree operation tables by pointer equality. The realtime additions are `xfs_btree_is_rtrmap`, `xfs_btree_is_rtrefcount`, and optional `xfs_btree_is_mem_rtrmap`. These predicates let generic btree code specialize behavior without embedding type-specific enums in every call path.

Transaction flags define common state such as dirty transactions, superblock dirtiness, permanent log reservations, synchronous commit, reserve pool use, no-writecount transactions, freed-block reservations, intent-done presence, lowmode allocation, and `XFS_TRANS_RTBITMAP_LOCKED`.

The `xfs_trans_mod_sb` field constants include normal counters and geometry fields plus `XFS_TRANS_SB_RGCOUNT`, which records realtime group count updates. Buffer reference constants include `XFS_REFC_BTREE_REF` and `XFS_RMAP_BTREE_REF` used by refcount/rmap btree buffer cache behavior.

`struct xfs_ino_geometry` describes computed inode allocation and inobt geometry: maximum inode count, cluster sizes, alignment, inobt capacities and levels, allocation sizes, sparse allocation minimums, stripe inode alignment, AG inode bit width, default attr fork offset, default inode flags2, and minimum folio order.
