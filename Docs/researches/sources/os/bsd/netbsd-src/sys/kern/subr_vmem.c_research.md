# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_vmem.c

Read completely: 1941 lines.

This file implements NetBSD's `vmem` arbitrary-resource allocator, based on Bonwick-style vmem arenas. It manages address/resource spans with boundary tags, segregated free lists, a hash of busy allocations, import/release callbacks to parent arenas, optional small-allocation quantum caches, DDB/debug support, and a standalone unit-test build.

Core data model:
- Boundary tags represent static spans, imported spans, free regions, and busy allocations.
- Free tags are organized by size order in `vm_freelist[]`.
- Busy tags are indexed by address in `vm_hashlist`.
- `vm_seglist` preserves span order for coalescing and diagnostics.
- In-kernel boundary tags come from a special pool plus a static reserve to avoid allocator recursion.

Initialization:
- `vmem_bootstrap` initializes global locks and the static boundary-tag freelist.
- `vmem_subsystem_init` creates metadata arenas (`vmem-va`, `vmem-meta`) and the boundary-tag pool.
- `vmem_init`, `vmem_create`, and `vmem_xcreate` initialize arenas, optional qcache layers, hash state, initial spans, and global arena list membership.

Allocation/free:
- `vmem_alloc` rounds simple allocations and delegates to `vmem_xalloc`.
- `vmem_xalloc_addr` reserves an exact address range.
- `vmem_xalloc` enforces size/alignment/phase/nocross/min/max restrictions, preallocates tags, searches free lists by instant-fit or best-fit, imports new spans when possible, splits free regions, and inserts busy tags.
- `vmem_free` delegates to qcache or `vmem_xfree`.
- `vmem_xfree` finds the busy tag and calls `vmem_xfree_bt`.
- `vmem_xfree_bt` removes the busy tag, coalesces adjacent free tags, optionally releases whole imported spans to the parent, wakes waiters, and trims excess free boundary tags.
- `vmem_xfreeall` frees all busy allocations for non-qcache arenas.

Maintenance/debug:
- `vmem_rehash_start` schedules a periodic workqueue/callout that resizes busy hash tables based on observed allocation counts.
- DDB helpers implement `vmem_whatis`, `vmem_printall`, and `vmem_print`.
- `VMEM_SANITY` checks overlapping/corrupt tags.
- `UNITTEST` builds a randomized allocator exerciser.

Integration: this allocator underpins virtual address and kernel metadata resource management. It uses UVM for backing metadata arenas, `pool` for boundary tags, `workqueue` for rehashing, and `uvm_kick_pdaemon` on memory pressure.

Reliability notes: many correctness properties are enforced by `KASSERT`, including quantum alignment and exact free sizes. The allocation path has comments noting limitations around importing regions under min/max or alignment restrictions. Boundary-tag reserve logic is critical: failures or lock-order regressions here can deadlock low-memory paths.
