# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_biomem.c

Read completely: 315 lines.

Implements the memory-management side of OpenBSD buffers: reservation and reuse of kernel virtual address slots, mapping buffer pages into KVA, deferred freeing when KVA cannot be immediately reclaimed, and allocation/freeing of DMA-reachable buffer pages.

KVA reservation and mapping:
- `buf_mem_init()` reserves a contiguous `PROT_NONE` range in `kernel_map` for buffer mappings and initializes available KVA slot counters based on `MAXPHYS`.
- `buf_acquire()` marks a buffer busy and maps it.
- `buf_acquire_nomap()` marks a buffer busy while preserving any existing mapping and removing it from the available-KVA list.
- `buf_map()` assigns KVA to a buffer, first from unallocated reserved space, then by stealing an idle mapped buffer from `buf_valist`.
- Non-cleaner/non-syncer callers wait on `buf_needva` when KVA slots fall below `RESERVE_SLOTS`.
- Mapping inserts each buffer page with `pmap_kenter_pa()` and updates the kernel pmap.

Release and unmap behavior:
- `buf_release()` clears `B_BUSY`, places mapped buffers onto `buf_valist`, increments available KVA slots, and wakes KVA waiters.
- `buf_unmap()` removes an idle buffer mapping, returns its KVA address for reuse, and finally frees buffers marked `B_RELEASED`.
- `buf_dealloc_mem()` removes mappings, frees pages, and if KVA existed defers `pool_put()` by marking `B_RELEASED` and putting the buffer at the front of `buf_valist`.
- `buf_fix_mapping()` shrinks an existing mapping after clustered reads split one large mapping across multiple buffers.

Page allocation:
- `buf_alloc_pages()` initializes a buffer UVM object and allocates wired pages with DMA constraints.
- It first tries NOWAIT allocation, then asks `bufbackoff()` to recover clean cache pages, then falls back to WAITOK allocation.
- `buf_free_pages()` unwires and accounts each page, clears the buffer page object fields, and frees the UVM object.

Risks and notes:
- The KVA slot accounting in `bcstats.kvaslots_avail` and `bcstats.busymapped` must remain paired with `buf_valist` mutations.
- `buf_dealloc_mem()` temporarily clears `b_data` because many assertions expect unmapped buffers to have null data pointers.
- Deferred release via `B_RELEASED` means a buffer structure can survive page freeing until its KVA mapping is stolen.
- Buffer pages are allocated with DMA reachability assumptions; changing constraints can break block-device I/O.
- Most routines require `splbio()` and assume callers have already serialized buffer state.
