# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ndifm.c

## Purpose

`ndifm.c` implements nexus-driver support for illumos DDI fault management. It manages per-child access/DMA handle caches, dispatches child error handlers, sets handle error state, and calls parent bus fault-management operations.

Read completely: 753 lines.

## Main Responsibilities

- Creates the global FM cache-entry kmem cache.
- Allocates and destroys per-device FM resource caches.
- Inserts and removes protected access and DMA handles from child FM caches.
- Matches bus error state against cached access/DMA handles.
- Sets access/DMA handle error state and invokes child error handlers.
- Dispatches registered child FM handlers for nexus errors.
- Calls parent bus `fm_init`, `fm_fini`, `fm_access_enter`, and `fm_access_exit` operations.

## Key Data Structures

- `ndi_fm_entry_cache`: global `kmem_cache_t` for `ndi_fmcentry_t`.
- `ndi_fmc_t`: per-device FM cache with lock, head, and tail.
- `ndi_fmcentry_t`: cached handle record containing resource pointer, bus-specific data, and list links.
- `i_ddi_fmhdl`: per-device FM handle state with capability flags, DMA/access caches, child targets, and FM kstats.
- `i_ddi_fmtgt`: child FM target entry with child dip and registered error handler.

## Cache Lifecycle And Handle Tracking

`ndi_fm_init()` creates the entry cache. `i_ndi_fmc_create()` allocates a cache and initializes its lock with the nexus-provided interrupt block cookie. `i_ndi_fmc_destroy()` frees remaining entries, destroys the lock, and frees the cache.

`ndi_fmc_insert()` checks the child FM capabilities, allocates an entry without sleeping, records resource and bus-specific data, stores the backpointer in the access or DMA handle error structure, and appends the entry to the cache list under `fc_lock`.

`ndi_fmc_remove()` finds the entry from the handle's stored `err_fep`, clears that handle pointer, unlinks the cache entry under `fc_lock`, and frees it. Capability mismatches increment or post FM diagnostics depending on access versus DMA cases.

## Error Matching

`ndi_fmc_entry_error()` scans a single child's matching cache. For each cached resource with a compare callback, it calls the callback with the bus error state. Fatal and nonfatal matches set the resource's FM error state, retrieve the updated error record, and attach the matching access or DMA handle to the `ddi_fm_error_t`.

`ndi_fmc_error()` enters the parent FM handler critical section, walks all registered child targets or a single target, calls `ndi_fmc_entry_error()` for each child cache, and invokes the child's registered error handler when a cached resource matched. It returns fatal if any fatal result occurred, nonfatal if any nonfatal result occurred, otherwise unknown.

`ndi_fmc_entry_error_all()` is a broader helper that marks all cached FLAGERR resources as nonfatal unexpected errors and returns nonfatal if anything was marked.

## Handler Dispatch And Busops

`ndi_fm_handler_dispatch()` invokes registered child error handlers for a nexus, either all targets or one target. It aggregates return statuses with fatal dominating nonfatal, nonfatal dominating unknown, and OK only if all handlers return OK.

`ndi_fm_acc_err_set()` and `ndi_fm_dma_err_set()` are simple wrappers around internal access/DMA error setters.

`i_ndi_busop_fm_init()` calls the parent bus `bus_fm_init()` if available and busops revision is high enough, returning system FM capabilities for the root node. `i_ndi_busop_fm_fini()` calls parent cleanup if present. `i_ndi_busop_access_enter()` and `i_ndi_busop_access_exit()` call parent exclusive-access busops for cautious access handles.

## Locking And Context

- FM cache lists are protected by each cache's `fc_lock`.
- Cache entry allocation uses `KM_NOSLEEP`, matching fault/error-path constraints.
- Handler dispatch is bracketed by `i_ddi_fm_handler_enter()` and `i_ddi_fm_handler_exit()`.
- Comments state insert/remove may be called from user or kernel context at or below `LOCK_LEVEL`; error scans may run in contexts permitted by the initialized interrupt block cookie.
- Removing a resource relies on the handle-stored entry pointer rather than searching by resource.

## Notable Edge Cases

- If a DMA-capable or access-capable child lacks the required capability, insert/remove returns early; access mismatch posts a driver ereport.
- Allocation failure increments the FM cache full kstat and silently leaves the resource uncached.
- Removing a missing cache entry increments the FM cache miss kstat.
- `ndi_fmc_error()` can invoke both cache comparison logic and child handlers, so a child may influence final status twice.
- Root node FM init returns system FM plus ereport capability without parent busops.

## Research Relevance

This file is important for storage and filesystem reliability research because nexus fault management is how bus, DMA, and programmed-I/O errors are associated with child device handles. Block-device drivers and storage HBAs rely on these paths to surface fatal or nonfatal I/O fault information.
