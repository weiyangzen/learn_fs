# File Research: sources/os/linux/linux/fs/xfs/scrub/newbt.h

Defines new-btree staging structures and public helpers.

Structures:
- `struct xrep_newbt_resv` records one reserved extent: list link, per-AG reference, autoreap state, AG block start, length, and used block count.
- `struct xrep_newbt` records scrub context, optional custom allocator, reservation list, fake btree root, owner info, bulk-load geometry, allocation hint, and reservation type.

Public API:
- Initialization: `xrep_newbt_init_bare`, `xrep_newbt_init_ag`, `xrep_newbt_init_inode`, `xrep_newbt_init_metadir_inode`.
- Space management: `xrep_newbt_alloc_blocks`, `xrep_newbt_add_extent`, `xrep_newbt_cancel`, `xrep_newbt_commit`.
- Bulk-loader integration: `xrep_newbt_claim_block`.
- Accounting: `xrep_newbt_unused_blocks`.

This header is used by repair code that rebuilds btrees with staged fake roots before atomically installing them.
