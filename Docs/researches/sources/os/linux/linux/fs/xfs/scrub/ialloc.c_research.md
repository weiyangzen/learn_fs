# File Research: sources/os/linux/linux/fs/xfs/scrub/ialloc.c

Scrubs the inode allocation btrees: inobt and finobt. It validates btree records, sparse inode hole masks, free masks, inode cluster buffers, alignment rules, and cross-references with the other inode btree plus rmap/free/refcount state.

Main components:
- `xchk_setup_ag_iallocbt` enables intent draining when needed and sets up AG btree scrub.
- `struct xchk_iallocbt` tracks scanned inode count and expected sequencing for geometries where one inode cluster spans multiple inobt records.
- `xchk_inobt_xref_finobt` and `xchk_finobt_xref_inobt` compare per-inode free/hole state between inobt and finobt, accounting for finobt omission rules.
- `xchk_iallocbt_chunk` validates the block range for a chunk, verifies it is used inode space, cross-references the opposite btree, rmap ownership, sharing, and CoW staging.
- `xchk_iallocbt_check_cluster_ifree` compares each inode’s allocation state from icache or disk against the inobt free mask.
- `xchk_iallocbt_check_cluster` validates cluster-level holemask consistency, maps the inode cluster buffer, and checks all contained dinodes.
- `xchk_iallocbt_rec_alignment` enforces inobt/finobt record alignment rules, including multi-record clusters.
- `xchk_iallocbt_rec` converts and validates a btree record, handles sparse/non-sparse records, checks hole/free count consistency, then checks clusters.
- `xchk_iallocbt_xref_rmap_btreeblks` compares counted inobt/finobt blocks with rmap-owned inode-btree blocks.
- `xchk_iallocbt_xref_rmap_inodes` compares inode blocks implied by inobt records with rmap-owned inode blocks.
- `xchk_iallocbt` selects the correct cursor, runs generic btree scrub, and performs rmap cross-references.
- `xchk_xref_is_not_inode_chunk` and `xchk_xref_is_inode_chunk` provide extent-to-inode-btree cross-reference helpers for other scrubbers.

Important invariants:
- Inobt must cover allocated inode chunks; finobt only tracks chunks with free inodes and can omit fully allocated/fully free/hole-only cases.
- Sparse inode holemask bits must map whole cluster subranges.
- Dinode magic and v3 inode number must match the btree-implied inode.
- Inode chunk space must be owned only by inode rmap records, not shared, and not CoW staging.
