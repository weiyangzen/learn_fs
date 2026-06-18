# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc.c

This file scrubs the inode allocation btrees: inobt and finobt. It validates record geometry, sparse inode masks, inode cluster contents, free/allocated state, and cross-references against each other and the rmap btree.

Setup:
- `xchk_setup_ag_iallocbt` enables intent draining when needed and then sets up AG btree scrub. Try-harder mode affects setup behavior.

Scrub state:
- `struct xchk_iallocbt` tracks total inodes observed and expected record sequencing for large cluster geometries.

Record checks:
- `xchk_iallocbt_rec` converts btree records to incore form, validates with `xfs_inobt_check_irec`, checks alignment, counts inodes, handles sparse and non-sparse records, and validates clusters.
- `xchk_iallocbt_rec_alignment` enforces inobt and finobt alignment rules, including multi-record inode clusters.
- `xchk_iallocbt_chunk` validates block ranges, checks used-space ownership, cross-references peer btrees, and rejects shared/COW staging ownership.

Inode cluster checks:
- `xchk_iallocbt_check_cluster` maps each inode cluster buffer, validates holemask consistency, checks rmap ownership, and reads cluster buffers.
- `xchk_iallocbt_check_cluster_ifree` compares inobt free bits with incore inode allocation state or on-disk `di_mode` fallback.

Inobt/finobt cross-reference:
- `xchk_inobt_xref_finobt` and `xchk_finobt_xref_inobt` compare free/hole state one inode at a time.
- Finobt may omit records for fully allocated, fully free, or hole-only cases as documented in the code.

Rmap cross-reference:
- `xchk_iallocbt_xref_rmap_btreeblks` verifies rmap-owned inobt/finobt btree block counts.
- `xchk_iallocbt_xref_rmap_inodes` verifies inode chunk blocks seen in inobt match rmap `OWN_INODES`.

Exported xref helpers:
- `xchk_xref_is_not_inode_chunk`
- `xchk_xref_is_inode_chunk`

Risks and edge cases:
- Incore-vs-disk inode state can require `-EDEADLOCK` if try-harder was not requested.
- Sparse inode holemask validation must match cluster allocation exactly.
- Corrupt peer btree cursors can be dropped through scrub xref handling, limiting follow-on checks.
