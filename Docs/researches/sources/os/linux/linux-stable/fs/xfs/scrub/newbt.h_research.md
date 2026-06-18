# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.h

This header declares the replacement-btree builder used by online repair.

Key structures:
- `struct xrep_newbt_resv`
  - reservation list link
  - perag reference
  - autoreap state
  - AG block start, length, and used count
- `struct xrep_newbt`
  - scrub context
  - optional custom allocator
  - reservation list
  - fake AG or inode btree root
  - rmap owner info
  - btree bulk-load geometry
  - allocation hint
  - per-AG reservation type

Exported operations:
- Initialize for bare, AG, inode, or metadir inode use.
- Allocate blocks or add a known extent.
- Cancel or commit reservations.
- Claim a block for btree bulk loading.
- Query unused blocks.

Integration:
- Used by repair modules that rebuild btrees into staged fake roots before atomically committing new roots.
- Exposes enough hooks for callers to plug custom allocation and bload record providers.
