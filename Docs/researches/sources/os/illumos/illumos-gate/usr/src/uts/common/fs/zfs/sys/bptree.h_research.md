# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bptree.h

Read status: complete, 65 lines.

Purpose: persistent tree/list of block pointers with birth-TXG and traversal-resume metadata, used for deferred block processing.

Key structures and APIs:
- `bptree_phys_t` records begin/end counters and byte/compressed/uncompressed totals.
- `bptree_entry_phys_t` stores a `blkptr_t`, a minimum birth TXG for deletion eligibility, and a `zbookmark_phys_t` resume point.
- `bptree_alloc()`, `bptree_free()`, `bptree_is_empty()` manage object lifecycle.
- `bptree_add()` records a block pointer and accounting.
- `bptree_iterate()` processes entries, optionally freeing them.

Dependencies: SPA block pointers, ZIO bookmarks, DMU transactions.

Research notes:
- Similar role to `bpobj`, but with per-entry traversal resume support.
- Used by asynchronous destroy/deferred free flows.
