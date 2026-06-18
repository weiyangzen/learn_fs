# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kmem.c

## Purpose

`kmem.c` implements the illumos kernel memory allocator: Bonwick slab caches, per-CPU magazines, vmem-backed heap arenas, allocator debugging, allocation logs, cache kstats, low-memory reaping, crash-dump-safe allocation diversion, and slab consolidation by object move callbacks.

Read completely: 5,459 lines.

## Main Responsibilities

- Provides the public kernel allocation interfaces: `kmem_alloc()`, `kmem_zalloc()`, `kmem_free()`, `kmem_rezalloc()`, `kmem_cache_create()`, `kmem_cache_destroy()`, `kmem_cache_alloc()`, and `kmem_cache_free()`.
- Builds size-indexed allocation caches for normal `kmem_alloc()` requests and routes oversize allocations to `kmem_oversize_arena`.
- Manages slab lifecycle: creates slabs from a cache vmem arena, carves buffers, tracks allocated buffers through embedded or hashed bufctls, and returns empty slabs to vmem.
- Implements per-CPU magazine fast paths plus central full/empty depots for scalable allocation and free.
- Supports allocator diagnostics: redzones, deadbeef/freed patterns, buftags, transaction/content/failure/slab/zero-size logs, stack capture, corruption classification, and panic/debug-entry policy.
- Publishes per-cache kstats and heap availability helpers.
- Reaps caches under memory pressure and periodically resizes hash tables, grows magazine sizes on contention, and scans for fragmentation.
- Supports the slab consolidator, where clients may register move callbacks so kmem can relocate live objects off sparse slabs.
- Diverts allocations during crash dumps to pre-reserved dump-safe memory so heap state remains stable while dumping.
- Initializes the allocator across boot phases, after `/etc/system` tunables are read, and starts maintenance taskqs and periodic update callbacks.

## Important Data Structures And Globals

- `kmem_cache_t`: cache descriptor containing object size/alignment, flags, vmem source, constructors/destructors, slab lists, per-CPU caches, depot lists, hash table, kstat, and optional defrag state.
- `kmem_slab_t`: slab descriptor with cache pointer, free buffer head, base address, chunk/ref counts, partial-slab ordering flags, and consolidator state.
- `kmem_bufctl_t` / `kmem_bufctl_audit_t`: buffer control metadata; audit form records timestamp, thread, stack, content snapshot pointer, cache, slab, and address.
- `kmem_magazine_t`, `kmem_magtype_t`, `kmem_cpu_cache_t`, and `kmem_maglist_t`: magazine-layer objects for CPU-local and depot caching.
- `kmem_defrag_t` and `kmem_move_t`: per-cache consolidation state and pending move callback records.
- `kmem_alloc_table` and `kmem_big_alloc_table`: lookup tables mapping request sizes to backing `kmem_alloc_*` caches.
- Global arenas: `kmem_metadata_arena`, `kmem_msb_arena`, `kmem_cache_arena`, `kmem_hash_arena`, `kmem_log_arena`, `kmem_oversize_arena`, `kmem_va_arena`, `kmem_default_arena`, and firewall arenas.
- Global taskqs: `kmem_taskq` for maintenance/reaping and `kmem_move_taskq` for serialized client move callbacks.

## Slab Layer

`kmem_slab_create()` allocates a slab from the cache arena, initializes it with the uninitialized pattern unless the cache is `KMC_NOTOUCH`, creates slab/bufctl metadata, sets optional redzones and free patterns, and links all buffers onto the slab free list. For hashed caches, slab and bufctl metadata are allocated from metadata caches; for compact no-hash caches, metadata is embedded in the slab/buffer layout.

`kmem_slab_alloc()` selects the first partial slab or creates a new one, removes one raw buffer, updates allocation counters, inserts hashed bufctls into the allocated-address hash table, and moves slabs between partial and complete lists. New slabs may be prefilled into magazines when the cache permits it.

`kmem_slab_free()` reverses the process: it finds and validates the buffer, updates audit/logging state, returns the buffer to the slab free list, moves complete slabs back to partial state, and destroys empty slabs. If move callbacks are pending, empty slabs are placed on a defrag deadlist rather than immediately unmapped, preserving the contract that callback buffers remain backed by memory touched only by kmem or the client.

## Magazine And Depot Layer

`kmem_cache_alloc()` first attempts the current CPU's loaded magazine, then the previous magazine, then a full depot magazine, and finally the slab layer. `kmem_cache_free()` mirrors this by returning to the loaded magazine, swapping with an empty previous magazine, obtaining/creating empty depot magazines, or falling through to slab free.

The depot tracks full and empty magazine working sets. `kmem_depot_ws_update()` snapshots minimum occupancy, `kmem_depot_ws_zero()` marks everything reapable, and `kmem_depot_ws_reap()` destroys magazines that fall outside the working set. Magazine size can grow when depot lock contention exceeds `kmem_depot_contention`.

## Debugging And Corruption Detection

Debug modes are controlled by `kmem_flags` and cache creation flags. They add combinations of:

- `KMF_AUDIT`: transaction stack/time logging.
- `KMF_DEADBEEF`: free-pattern verification and poisoning.
- `KMF_REDZONE`: write-past-end detection.
- `KMF_CONTENTS`: saved content snapshots.
- `KMF_LITE`: lower-overhead buftag history.
- `KMF_FIREWALL`: hardware-unmapped page after selected large buffers.

`kmem_error()` classifies allocator failures such as modified free buffers, redzone violations, duplicate frees, bad addresses, corrupted buftags/bufctls, wrong-cache frees, wrong-size frees, and bad base addresses. It records `kmem_panic_info`, prints diagnostic context, emits previous transaction stacks when available, then panics or enters the debugger depending on `kmem_panic`.

`kmem_alloc()` and `kmem_free()` store and validate the original requested size for debug-backed generic allocations, so freeing a cached buffer with the wrong size is reported separately from redzone corruption.

## Reaping And Maintenance

`kmem_reap()` and `kmem_reap_idspace()` throttle and dispatch asynchronous cache reaping. The memory-backed reap path asks each cache's owner reclaim callback for memory, reaps depot magazines, and invokes defrag if enabled. The identifier-space path limits work to caches backed by identifier arenas.

Periodic `kmem_update()` walks all caches and may dispatch:

- hash-table rescale work when allocated-buffer count diverges from hash size,
- magazine resize work when depot contention rises,
- slab-consolidator scans for movable caches.

`kmem_cache_reap_soon()` is a targeted API that zeroes one cache's depot working set and schedules a depot reap without waiting for completion.

## Slab Consolidator

The opening theory statement and implementation define cooperative defragmentation. Clients call `kmem_cache_set_move()` before allocation to install a move callback. Kmem then identifies sparse partial slabs and asks the client to move live objects to destination buffers that kmem has already allocated and constructed.

Client callback responses drive cleanup:

- `KMEM_CBRC_YES`: client moved the object; kmem frees the old buffer.
- `KMEM_CBRC_NO`: client refuses permanently; kmem frees the new buffer and marks the source slab non-movable until the stuck object is freed or notification clears it.
- `KMEM_CBRC_LATER`: temporary refusal; after repeated disbelief the slab is treated as non-movable.
- `KMEM_CBRC_DONT_NEED`: client discards the old object; kmem frees both buffers.
- `KMEM_CBRC_DONT_KNOW`: client cannot safely recognize the object; kmem frees the new buffer and relies on reaping/magazine draining.

`kmem_move_buffers()` scans backward from the least-used partial slabs, issues move requests while carefully dropping `cache_lock`, and uses `KMEM_SLAB_MOVE_PENDING` plus the deadlist to prevent slab destruction races. `kmem_cache_move_notify()` lets clients later report that a previously stuck object may now be movable.

## Initialization And Boot Phases

`kmem_init()` starts by initializing kstats and metadata arenas, creates a temporary allocator so `/etc/system` tunables can be read, destroys the temporary caches, then recreates arenas/caches with final tunables. It chooses large-page heap backing when appropriate, configures firewall thresholds, initializes logs, STREAMS messages, zones ZSD, taskq/logging, platform aligned allocation, ID caches, and netstack hooks.

`kmem_thread_init()` creates the move taskq and maintenance taskq. `kmem_mp_init()` registers CPU setup callbacks, starts periodic update scheduling, and finishes taskq MP initialization. `kmem_cpu_setup()` purges and re-enables magazines on CPU unconfiguration to keep per-CPU cache state valid.

## Crash Dump Allocation Diversion

`kmem_dump_init()` reserves a heap area for dump-time allocations. `kmem_dump_begin()` marks caches as dump-divertible or dump-unsafe based on their arena flags, disables current magazine rounds on the dumping CPU, and routes eligible allocations through `kmem_cache_alloc_dump()`. `kmem_cache_free_dump()` recycles constructed dump buffers in a simple freelist or suppresses normal frees while the reserved area is available. `kmem_dump_finish()` reports reserved-area exhaustion and optional usage statistics.

## Notable Risks And Invariants

- The allocator relies on strict lock ordering: per-cache locks, per-CPU locks, depot locks, global cache linkage, and taskq serialization are carefully separated.
- Cache constructors and destructors must obey strong contracts; destructors must tolerate newly constructed objects, and move callbacks must not free either buffer passed to them.
- Debug behavior can change object layout and allocation routing, especially for firewalled and buftagged caches.
- Empty slab destruction is intentionally deferred when move callbacks are pending; violating this would break client recognition assumptions and could expose unmapped memory during callbacks.
- `kmem_alloc(0, KM_SLEEP)` is treated as deprecated and is optionally warned or panicked, while non-sleeping zero-size allocation returns `NULL`.

## Research Relevance

For filesystem and storage research, this file defines the allocator contracts used by vnode caches, buffer caches, transaction objects, ZFS structures, task queues, and driver/storage metadata. The reclaim callback model, cache kstats, low-memory reaping, and slab-consolidator move contract are especially relevant to long-lived filesystem objects and memory-pressure behavior.
