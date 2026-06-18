# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bplist.h

Read status: complete, 57 lines.

Purpose: in-memory linked list wrapper for `blkptr_t` values.

Key structures and APIs:
- `bplist_entry_t` stores one block pointer plus list linkage.
- `bplist_t` stores a mutex and list head.
- `bplist_itor_t` is an iterator callback receiving a block pointer and transaction.
- `bplist_create()`, `bplist_destroy()`, `bplist_append()`, and `bplist_iterate()` manage list lifecycle and traversal.

Dependencies: `zfs_context.h`, `spa.h`, `dmu_tx_t`.

Research notes:
- Used for pending deadlists and other transient collections of block pointers.
- The interface is memory-resident and transaction-aware only through iterator callbacks.
