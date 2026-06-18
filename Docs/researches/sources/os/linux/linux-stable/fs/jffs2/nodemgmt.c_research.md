# File Research: sources/os/linux/linux-stable/fs/jffs2/nodemgmt.c

This file manages JFFS2 physical node allocation, active eraseblock selection, obsolete-node accounting, and garbage-collection wakeup policy.

Key responsibilities:
- Enforces reserved-pool write policy in `jffs2_rp_can_write()`, allowing privileged writers through `CAP_SYS_RESOURCE` when normal free/dirty/unchecked/erasing space drops below the configured pool.
- Implements `jffs2_reserve_space()` for normal/deletion allocations, including allocation semaphore ownership, free-block pressure checks, GC triggering, erase-wait sleeps, signal interruption, and raw-node-ref preallocation.
- Implements `jffs2_reserve_space_gc()` for GC allocations without taking `alloc_sem`.
- Selects and retires `c->nextblock` through `jffs2_find_nextblock()` and `jffs2_close_nextblock()`, moving eraseblocks among `free_list`, `clean_list`, `dirty_list`, `very_dirty_list`, `erasable_list`, `erase_pending_list`, and write-buffer-pending erase lists.
- Handles summary-aware reservations in `jffs2_do_reserve_space()`, writing summary nodes before a block becomes too full when summary collection is active.
- Handles no-summary tail waste by linking an obsolete raw-node ref over unusable trailing space and converting its accounting from dirty to wasted.
- Adds freshly written nodes through `jffs2_add_physical_node_ref()`, enforcing contiguous placement at the current write offset and filing full clean blocks.
- Completes reservations in `jffs2_complete_reservation()` by triggering GC and releasing `alloc_sem`.
- Marks nodes obsolete in `jffs2_mark_node_obsolete()`, updating used/unchecked/dirty/wasted accounting, refiling eraseblocks, optionally clearing the on-flash accurate bit, and unlinking obsolete refs from inode or xattr ownership lists when safe.
- Decides whether the background GC thread should wake in `jffs2_thread_should_wake()` based on pending erases, unchecked nodes, low free block counts, and very-dirty block thresholds.

Important interactions:
- Relies on `erase_completion_lock` for block-list and accounting transitions, `alloc_sem` for single active allocation, and `erase_free_sem` to keep refs stable while physically marking obsolete nodes.
- Calls into GC, erase, summary, write-buffer, raw-node-ref, inode-cache, and xattr subsystems.
- Uses `jffs2_can_mark_obsolete()` and read-only/building/scanning flags to distinguish NOR-style physical obsoletion from NAND/summary modes where deletion nodes and in-memory accounting carry more of the burden.

Notable invariants and risks:
- Non-obsolete writes must be appended at `nextblock`'s current free offset; violations are treated as allocator corruption.
- Space-accounting counters must remain balanced across superblock and per-eraseblock totals; this file deliberately runs paranoia checks after major transitions.
- `jffs2_mark_node_obsolete()` has several mode-dependent exits; lock ownership differs depending on whether physical obsoletion is possible.
- GC can be forced when free blocks are insufficient, but the code guards against endless GC loops by comparing dirty/possibly-available space against reserved thresholds.
