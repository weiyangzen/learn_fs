# File Research: sources/os/linux/linux/fs/jffs2/nodemgmt.c

## Role

Manages JFFS2 physical node allocation, active eraseblock selection, obsolete-node accounting, block-list transitions, and garbage-collection wakeup policy.

## Key Responsibilities

- Enforces reserved-pool write policy in `jffs2_rp_can_write()`, allowing normal writes only when available reclaimable/free space exceeds `rp_size`, with `CAP_SYS_RESOURCE` override.
- Implements normal/deletion reservations in `jffs2_reserve_space()`, including `alloc_sem` ownership, low-space checks, GC passes, erase-wait sleeps, signal interruption, and raw-node-ref preallocation.
- Implements GC reservations in `jffs2_reserve_space_gc()` without taking `alloc_sem`.
- Selects and retires `c->nextblock` through `jffs2_find_nextblock()` and `jffs2_close_nextblock()`.
- Handles summary-aware reservation through `jffs2_do_reserve_space()`, writing summary nodes before an eraseblock becomes too full.
- Converts unusable tail space into obsolete raw-node refs when summaries are disabled or inactive.
- Adds committed nodes through `jffs2_add_physical_node_ref()`, enforcing contiguous placement at the current append point.
- Marks nodes obsolete in `jffs2_mark_node_obsolete()`, updating used/unchecked/dirty/wasted accounting, refiling eraseblocks, optionally clearing the on-flash accurate bit, and detaching obsolete refs from inode or xattr ownership lists when safe.
- Determines whether the background GC thread should wake in `jffs2_thread_should_wake()`.

## Important Interactions

- Uses `erase_completion_lock` for eraseblock lists and accounting.
- Uses `alloc_sem` to serialize active allocations.
- Uses `erase_free_sem` when physical obsoletion is possible so erasure cannot free refs while the obsolete bit is being written.
- Calls GC, erase, summary, write-buffer, raw-node-ref, inode-cache, and xattr helpers.

## Invariants and Risks

- Non-obsolete writes must append at `nextblock`'s current free offset; mismatches are allocator corruption.
- Space counters are balanced at both filesystem and eraseblock granularity and checked with debug paranoia helpers.
- Physical obsoletion depends on flash/writebuffer/summary/read-only/building/scanning state.
- Low-space loops guard against endless GC by checking both dirty space and maximum possible available space.
