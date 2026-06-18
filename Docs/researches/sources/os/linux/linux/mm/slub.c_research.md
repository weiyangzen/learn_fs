# File Research: sources/os/linux/linux/mm/slub.c

## File Role

`sources/os/linux/linux/mm/slub.c` is the Linux SLUB slab allocator implementation. It provides the core fixed-size object allocator behind `kmem_cache_alloc()`, `kmalloc()`, `kfree()`, bulk allocation/free APIs, large-kmalloc fallback handling, cache creation/shutdown, NUMA slab-node management, debug validation, sysfs/debugfs observability, and boot-time SLUB initialization.

The implementation is heavily conditional on kernel configuration: `CONFIG_SLUB_DEBUG`, `CONFIG_NUMA`, `CONFIG_MEMCG`, `CONFIG_SLAB_OBJ_EXT`, `CONFIG_SLAB_FREELIST_RANDOM`, `CONFIG_SLAB_FREELIST_HARDENED`, `CONFIG_KASAN`, `CONFIG_KMSAN`, `CONFIG_KFENCE`, `CONFIG_PREEMPT_RT`, `CONFIG_SLUB_STATS`, and related debug/accounting options.

## Core Model

SLUB manages memory as `struct slab` pages owned by a `struct kmem_cache`. Each slab contains a sequence of same-sized objects and a freelist of available objects. The file distinguishes these slab states:

- Node partial slab: has free objects and is on the per-node partial list.
- Removed partial slab: isolated from the node list, usually to take its freelist.
- Full slab: all objects in use; normally not listed unless debug tracking needs a full list.
- Frozen slab: metadata consistency failed; treated as unavailable and leaked rather than reused.

This version uses per-CPU "sheaves" as its primary fast-path cache. Each CPU has `main`, `spare`, and `rcu_free` sheaves in `struct slub_percpu_sheaves`, while each NUMA node can have a shared `struct node_barn` holding full and empty sheaves. Allocations normally pop objects from the current CPU main sheaf. Frees normally push objects into the current CPU main sheaf. Barns trade full and empty sheaves between CPUs on the same node, reducing direct partial-list and page-allocator traffic.

## Main Data Structures

Important file-local structures:

- `struct kmem_cache_node`: per-NUMA-node slab lists, including `partial`, optional debug `full`, `nr_partial`, and debug slab/object counters.
- `struct slab_sheaf`: flexible-array object pointer batch used for fast allocation/free, prefill APIs, and RCU free batching.
- `struct slub_percpu_sheaves`: per-CPU sheaf state protected by `local_trylock_t`.
- `struct node_barn`: per-node pool of full and empty sheaves protected by a spinlock.
- `struct track`: debug allocation/free provenance, including caller address, optional stackdepot handle, CPU, PID, and timestamp.
- `struct partial_context` and `struct partial_bulk_context`: parameter carriers for partial-list allocation/refill paths.
- `struct detached_freelist`: transient freelist assembled during bulk free so a batch of objects from one slab can be returned with one synchronization sequence.

Key global state includes `slab_nodes`, `slab_barn_nodes`, `flushwq`, per-CPU `slub_flush`, global SLUB order tunables, `kmem_cache_node`, and sysfs/debugfs registration state.

## Allocation Paths

The primary exported object allocation APIs are:

- `kmem_cache_alloc_noprof()`
- `kmem_cache_alloc_lru_noprof()`
- `kmem_cache_alloc_node_noprof()`
- `kmem_cache_alloc_bulk_noprof()`
- `kmem_cache_alloc_from_sheaf_noprof()`
- `__kmalloc_noprof()`
- `__kmalloc_node_noprof()`
- `__kmalloc_cache_noprof()`
- `__kmalloc_cache_node_noprof()`
- `__kmalloc_large_noprof()`
- `__kmalloc_large_node_noprof()`
- `kmalloc_nolock_noprof()`

The normal allocation flow is `slab_alloc_node()`:

1. `slab_pre_alloc_hook()` applies allowed GFP mask, `might_alloc()`, and failslab injection.
2. `kfence_alloc()` may intercept.
3. `alloc_from_pcs()` tries the per-CPU sheaf fast path.
4. `__slab_alloc_node()` / `___slab_alloc()` falls back to partial slabs or new slab pages.
5. `maybe_wipe_obj_freeptr()` clears object-embedded freelist state if needed.
6. `slab_post_alloc_hook()` performs KASAN tagging/init, optional zeroing, kmemleak, KMSAN, allocation profiling, and memcg post-charge.

Slow allocation first tries a local or requested-node partial list via `get_from_partial()`. On NUMA systems it may use remote partial slabs according to `remote_node_defrag_ratio`, cpuset constraints, and memory policy. If no partial slab works, `new_slab()` allocates pages, initializes object freelists, debug metadata, KASAN state, slab object extensions, accounting, and optional freelist randomization.

Bulk allocation uses `alloc_from_pcs_bulk()` first and falls back to `__kmem_cache_alloc_bulk()` / `refill_objects()`, which can detach whole freelists from partial slabs and allocate new slabs until the requested batch is filled.

## Free Paths

The primary exported free APIs are:

- `kmem_cache_free()`
- `kmem_cache_free_bulk()`
- `kfree()`
- `kfree_nolock()`
- `kvfree()`
- `kvfree_atomic()`
- `kvfree_sensitive()`
- `kvfree_rcu_cb()`

The normal free flow is `slab_free()`:

1. Run memcg and allocation-tag free hooks.
2. Run `slab_free_hook()` for kmemleak, KMSAN, lock/object debug checks, KCSAN, KFENCE, KASAN pre-free/quarantine, optional RCU debug delay, and init-on-free.
3. If the object is local-node and not pfmemalloc, try `free_to_pcs()`.
4. Otherwise fall back to `__slab_free()`.

`__slab_free()` is the central slow free. For debug/TINY caches it serializes through `free_to_partial_list()`. For normal caches it updates slab freelist/counters through double-word cmpxchg when available, or slab bit lock otherwise. It touches the per-node list lock only when a full slab becomes partial or a slab becomes empty enough to discard.

`kfree_nolock()` is a restricted NMI/raw-spinlock-safe path for objects allocated by `kmalloc_nolock()`. It skips hooks that are unsafe from those contexts and defers slow frees through per-CPU `irq_work` when direct sheaf free cannot complete.

## Sheaves And Barns

Sheaves are the dominant performance feature in this file. A cache's `sheaf_capacity` is computed from object size, disabled for debug/TINY/bootstrap/no-leaktrace cases, and rounded so the sheaf allocation itself fits a kmalloc bucket.

Important sheaf flows:

- `alloc_from_pcs()` pops from the CPU main sheaf.
- `__pcs_replace_empty_main()` swaps in the spare sheaf, gets a full sheaf from the barn, or refills a newly allocated sheaf from slabs.
- `free_to_pcs()` pushes into the CPU main sheaf.
- `__pcs_replace_full_main()` swaps spare, gets an empty sheaf, puts full sheaves into the barn, or flushes when limits are reached.
- `kmem_cache_prefill_sheaf()`, `kmem_cache_return_sheaf()`, and `kmem_cache_refill_sheaf()` expose explicit prefilled sheaf usage.
- `__kfree_rcu_sheaf()` batches RCU frees in a per-CPU sheaf and flushes by `call_rcu()` when full.
- `flush_all_cpus_locked()`, `flush_rcu_sheaves_on_cache()`, and CPU hotplug callbacks drain per-CPU sheaves.

Barns are per-node spinlock-protected exchange pools. They track bounded full and empty sheaf lists using `MAX_FULL_SHEAVES` and `MAX_EMPTY_SHEAVES`, with deliberate racy prechecks to avoid lock traffic.

## Slab Layout And Metadata

`calculate_sizes()` lays out each object inside a slab. It accounts for alignment, redzones, object poisoning, constructor constraints, RCU type safety, freelist pointer placement, allocation/free tracking records, original kmalloc request size, KASAN metadata, optional in-object slab object extensions, and final alignment padding.

The freelist pointer can be stored inside the object or after the object. `freeptr_outside_object()` and `get_info_end()` encode assumptions used by debug checks, zeroing, `ksize()`, and init-on-free behavior.

For hardening, freelist pointers can be XOR-obfuscated with a per-cache random value and the pointer storage address. Freelist randomization can also initialize per-cache random object orderings for newly allocated slabs.

## Debugging And Validation

With `CONFIG_SLUB_DEBUG`, this file implements:

- Redzone setup and checking.
- Object poisoning and padding validation.
- Allocation/free caller tracking with optional stackdepot.
- Slab and freelist consistency checks.
- Full-slab tracking for debuggable caches.
- KUnit error integration.
- `validate_slab_cache()` export.
- Detailed corruption reports via `slab_bug()`, `object_err()`, `slab_err()`, `print_trailer()`, and tracking dumps.
- `slab_debug=` / `slub_debug=` parser supporting flags for sanity checks, redzone, poison, store-user, trace, failslab, and higher-order debug avoidance.

On detected corruption, the allocator often repairs metadata enough to continue, but may mark a slab frozen, clear freelists, adjust object counts, or intentionally leak unsafe objects.

## Accounting, Sanitizers, And Hooks

The file integrates with:

- memcg slab charging and freeing through slab object extensions.
- allocation profiling through `slabobj_ext` and codetag references.
- KASAN allocation/free, quarantine, object tagging, large-kmalloc handling, and krealloc checks.
- KMSAN allocation/free hooks.
- KFENCE allocations and frees.
- kmemleak recursive allocation/free tracking.
- debugobjects and lock debugging.
- KCSAN use-after-free access assertions.
- page and lruvec slab byte accounting.

`alloc_slab_obj_exts()` can allocate extension vectors either from slab leftover space, inside objects, or externally, with guards against recursive self-pinning when profiling metadata would otherwise be allocated from the same cache.

## Kmalloc, Kvmalloc, And Realloc

`__do_kmalloc_node()` selects a kmalloc cache for small allocations and sends oversized requests to page allocator-backed large kmalloc. Large allocations are marked `PageLargeKmalloc` and freed by `free_large_kmalloc()`.

`ksize()` validates the object through KASAN before returning usable allocation size. It distinguishes large kmalloc, normal slab, KFENCE, debug redzone/poison restrictions, KASAN caches, RCU-safe caches, and in-object object extensions.

Reallocation is handled by:

- `krealloc_node_align_noprof()`
- `__do_krealloc()`
- `kvrealloc_node_align_noprof()`

These preserve content, account for original kmalloc request size when debug metadata exists, support alignment checks, and fall back from kmalloc to vmalloc when needed.

`__kvmalloc_node_noprof()` first tries physically contiguous kmalloc with adjusted GFP flags, then falls back to `__vmalloc_node_range_noprof()` for page-sized and larger requests.

## Cache Lifecycle And Boot

Boot setup proceeds through `kmem_cache_init()`:

1. Initialize node masks.
2. Create static boot caches for `kmem_cache_node` and `kmem_cache`.
3. Switch to partial slab state.
4. Bootstrap dynamic `kmem_cache` objects from the static boot caches.
5. Build kmalloc caches.
6. Bootstrap sheaves for normal kmalloc caches after kmalloc is usable.
7. Initialize freelist randomization.
8. Register CPU hotplug callbacks.

`do_kmem_cache_create()` initializes ordinary caches: flags, hardening random value, layout, cmpxchg mode, partial thresholds, per-CPU sheaves, NUMA node structures and barns, stats, random freelist sequence, sysfs, and debugfs entries.

Shutdown uses `__kmem_cache_shutdown()` to flush CPU sheaves, wait for RCU sheaves, shrink barns, free empty partial slabs, and report remaining allocated objects. `__kmem_cache_release()` frees random sequences, per-CPU sheaves, stats, node structures, and barns.

Memory hotplug callbacks create or shrink per-node structures when nodes come online or offline. CPU hotplug setup allocates missing barns and flushes dead CPU sheaves.

## Sysfs, Debugfs, And Proc Interfaces

When sysfs support is enabled, `slab_sysfs_init()` creates `/sys/kernel/slab` entries. Attributes expose sizes, object counts, partial slabs, sheaf capacity, constructors, aliases, alignment, reclaim flags, RCU destruction, shrink trigger, NUMA remote defrag ratio, failslab, KFENCE skip, debug flags, validation, and optional SLUB stats.

Debugfs support creates per-cache trace files for allocation and free locations when `SLAB_STORE_USER` is active. It aggregates tracking records by caller/stack/waste and reports counts, age, PID range, CPUs, nodes, and stack traces.

`get_slabinfo()` provides `/proc/slabinfo` data under debug builds.

## Concurrency And Locking

The file documents and implements strict lock ordering:

1. CPU hotplug lock.
2. `slab_mutex`.
3. Per-CPU sheaf local lock, barn lock, or node list lock.
4. Per-slab bit lock on architectures lacking double-word cmpxchg.
5. Debug object map lock.

Fast paths use `local_trylock_t` for per-CPU sheaves. Barns and node lists use IRQ-safe spinlocks. Slab freelist/counter updates use `try_cmpxchg_freelist()` when supported, otherwise a page-bit slab lock. PREEMPT_RT and NMI-sensitive paths have explicit restrictions and fallbacks.

The implementation relies on deliberate racy prechecks for performance, followed by locked or cmpxchg validation before mutating shared state. List-lock acquisition in `__slab_free()` is speculative and dropped if the cmpxchg loses.

## Notable Invariants

- `pcs->main` is always non-NULL when per-CPU sheaves are initialized; bootstrap sheaves force fast paths to fail safely.
- Slabs on node partial lists must have `SL_partial` set; removed or full/frozen slabs must not be treated as normal partials.
- Full slabs are not listed for normal caches, but debug caches may keep full lists for validation.
- Frozen slabs are full and exempt from list management.
- Objects from pfmemalloc slabs are not returned to normal sheaves.
- Remote-node objects are generally not cached in local per-CPU sheaves.
- Debug metadata flags affect mergeability and layout; cache merging must not violate fixed metadata offsets.
- `kmalloc_nolock()` and `kfree_nolock()` are only valid for their restricted paired use cases.

## Research Notes

This file is a high-value filesystem/OS research dependency because most VFS, inode, dentry, buffer, block, and filesystem metadata objects ultimately use these allocation APIs. Performance and failure behavior in filesystems can be strongly affected by SLUB cache sizing, NUMA policy, memcg accounting, KASAN/KMSAN/KFENCE/debug options, sheaf refill/flush behavior, and slab shrink paths.

For future analysis, cross-reference this file with `mm/slab_common.c`, `include/linux/slab.h`, `mm/internal.h`, memcg slab helpers, KASAN/KMSAN/KFENCE implementations, and filesystem cache users that create named `kmem_cache` instances.
