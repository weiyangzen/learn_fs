# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config.c

## Purpose

Implements dynamic physical memory configuration: adding memory, preparing/deleting memory spans, tracking delete handles, coordinating page relocation/collection, updating memsegs and memory lists, and notifying registered subsystems.

This is the core kernel memory DR implementation for adding/removing physical pages from the running system.

## Main Responsibilities

- Dynamically add physical memory and its `page_t` metadata.
- Reserve add/delete spans to prevent overlapping operations.
- Allocate and manage memory delete handles.
- Validate delete spans against installed memory, memsegs, cage/nonrelocatable pages, and architecture constraints.
- Start asynchronous memory delete threads.
- Relocate, page out, destroy, or collect pages from delete spans.
- Clean up deleted memsegs and remap deleted page metadata to dummy pages.
- Maintain `phys_install`, `phys_avail`, `physmax`, `physinstalled`, `total_pages`, `maxmem`, `physmem`, `availrmem`, and dump sizing.
- Register callback vectors for subsystems affected by physical memory add/delete.
- Split memsegs for partial delete operations.
- Manage reusable dynamic memseg virtual-address space.

## Major Entry Points

- `kphysm_add_memory_dynamic(pfn_t base, pgcnt_t npgs)`
  Adds a dynamic memory span. Handles span reservation, installed-memory insertion, page metadata allocation/mapping, memnode setup, page counter resize, memseg allocation/reuse, page initialization/freeing, global memory accounting, page coalescing, callbacks, DDI notification, and rollback on failures.

- `kphysm_del_gethandle(memhandle_t *xmhp)`
  Allocates a delete handle and enters `MHND_INIT`.

- `kphysm_del_span(memhandle_t handle, pfn_t base, pgcnt_t npgs)`
  Intersects requested span with `phys_install`, reserves non-overlapping delete spans, checks memseg coverage and relocatability, splits memsegs when needed, rejects `P_NORELOC` pages, and records page counts.

- `kphysm_del_span_query(pfn_t base, pgcnt_t npgs, memquery_t *mqp)`
  Reports installed, managed, and non-relocatable page counts and first/last non-relocatable PFNs.

- `kphysm_del_start(memhandle_t handle, void (*complete)(void *, int), void *complete_arg)`
  Starts asynchronous memory deletion in `delete_memory_thread()`.

- `kphysm_del_cancel(memhandle_t handle)`
  Requests cancellation and wakes the delete thread.

- `kphysm_del_status(memhandle_t handle, memdelstat_t *mdstp)`
  Reports delete progress from handle counters.

- `kphysm_del_release(memhandle_t handle)`
  Releases handles in init/done states and removes reserved spans.

- `pfn_is_being_deleted(pfn_t pfnum)`
  Allows other subsystems, notably the cage, to detect active deletion spans.

- `kphysm_setup_func_register()` / `kphysm_setup_func_unregister()`
  Register post-add, pre-delete, and post-delete callback vectors.

- `mem_config_init()`, `memseg_alloc()`
  Initialize and allocate `struct memseg` objects.

## Add-Memory Flow

`kphysm_add_memory_dynamic()`:

1. Reserves the target span in the transit list.
2. Adds the full incoming span to `phys_install`.
3. Allocates `page_t` metadata either externally through weak `memseg_alloc_meta()` or from the incoming memory itself.
4. Handles KPM granularity and metadata sizing.
5. Maps metadata pages into kernel VA and probes accessibility.
6. Adds memnode range and adjusts page counters.
7. Adds usable pages to `phys_avail`.
8. Reuses or allocates a `memseg`, initializes page structures, remaps metadata if needed.
9. Inserts memseg into `memsegs`, updates KPM state, rebuilds PFN hash, updates `total_pages`.
10. Frees new pages to the VM system.
11. Updates global memory counters, dump size, page coalescing, callbacks, lgroup generation, and DDI.
12. Unreserves the span.

Rollback is handled by `kphysm_addmem_error_undospan()` plus local cleanup for metadata mappings, memnodes, page counters, and allocated metadata.

## Delete-Memory Flow

Delete is handle based:

1. `kphysm_del_gethandle()` creates a handle.
2. `kphysm_del_span()` adds one or more non-overlapping installed spans to the handle transit list, validates all relevant memsegs, and may split memsegs to isolate the delete range.
3. `kphysm_del_start()` records completion callback and starts `delete_memory_thread()`.
4. `delete_memory_thread()` reserves `availrmem`, runs registered pre-delete callbacks, allocates span bitmaps, starts AIO cleanup helper, and repeatedly scans target PFNs.
5. Pages are collected by:
   - removing free pages from free/cache lists,
   - accounting retired pages,
   - relocating locked/modified pages,
   - destroying clean pages,
   - forcing `VOP_PUTPAGE()` for dirty file-backed pages,
   - retrying after delays when no progress is made.
6. On cancellation, collected pages are freed back and `availrmem` is restored.
7. On success, `kphysm_del_cleanup()` removes memsegs, remaps metadata, updates memory lists/counters, dump size, and lgroup generation.
8. Post-delete callbacks run, state becomes `MHND_DONE`, and completion callback is invoked.

## Key Data Structures

- `struct mem_handle`
  Delete operation handle with mutex, external id, state, transit spans, counters, callback, cancel flags, worker thread id, and collected deleted-page list.

- `struct memdelspan`
  PFN span plus bitmaps for collected and retired pages.

- `struct transit_list` / `transit_list_head`
  Global list of active reserved/delete spans. Prevents overlap between add/delete operations and exposes active collection state.

- `struct memseg`
  Kernel memory segment descriptors. Dynamic memsegs may include metadata in the memory being managed or use external metadata.

- `memseg_va_avail`, `memseg_delete_junk`, `memseg_edit_junk`
  Lists for reusable dynamic memseg VA, deleted boot metadata, and obsolete split memsegs retained for concurrent readers.

## State Machine

`mhnd_state_t`:

- `MHND_FREE`
- `MHND_INIT`
- `MHND_STARTING`
- `MHND_RUNNING`
- `MHND_DONE`
- `MHND_RELEASE`

APIs enforce sequence. Release is refused while delete is starting/running; start is refused without spans or after completion.

## Locking and Synchronization

- `mem_handle_list_mutex` protects global handle list and handle id generation.
- Each `mem_handle` has `mh_mutex` for state, counters, cancellation, and worker coordination.
- `transit_list_head.trh_lock` protects span reservation and active collection visibility.
- `memsegs_lock()` protects global memseg list updates.
- `memseg_lists_lock` protects reusable/junk memseg side lists.
- `memlist_write_lock/read_lock` protects `phys_install` and `phys_avail`.
- `freemem_lock` protects `maxmem`, `physmem`, `availrmem`, and related counters.
- `mem_callback_rwlock` protects callback registry; pre-delete holds the reader lock until post-delete.
- Page deletion uses page locks, reclaim locks, group page locks, iolocks, vnode holds, HAT unload, and condition-variable wakeups for page waiters.
- CPU VM memseg caches are invalidated under `cpu_lock` with paused CPUs.

## Special Mechanisms

- Weak metadata provider hooks:
  `memseg_alloc_meta`, `memseg_free_meta`, `memseg_get_metapfn`, `memseg_remap_meta`.

- Dummy page metadata remapping:
  `memseg_remap_init()`, `remap_to_dummy()`, `memseg_remap_to_dummy()` create read-only dummy `page_t` backing for deleted metadata ranges so stale references do not point into removed memory.

- AIO cleanup helper:
  `dr_aio_cleanup_thread()` repeatedly invokes kaio cleanup for processes to break delete/kaio page-lock dependency cycles.

- Memseg split:
  `kphysm_split_memseg()` creates low/mid/high memseg replacements for partial deletes and leaves old memseg in edit junk for concurrent readers.

## External Dependencies

Memlists, memnodes, HAT/KPM, page relocation, page counters, kernel cage (`P_NORELOC`, `pfn_is_being_deleted()` interaction), DDI memory updates, dump subsystem, lgroup, pageout scanner, vnode putpage, kaio module, CPU pause/resume, and architecture-specific delete-span validation.

## Research Notes

This file is the dynamic memory hotplug/delete coordinator. Highest-risk areas are rollback after partial add failure, delete cancellation after collecting pages, stale memseg readers during split/delete, callback lock lifetime from pre-delete to post-delete, and ensuring no cage/nonrelocatable page enters a delete span after validation.
