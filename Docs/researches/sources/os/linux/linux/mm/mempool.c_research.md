# File Research: sources/os/linux/linux/mm/mempool.c

## Purpose

Implements Linux mempools: small preallocated reserve pools used to guarantee forward progress for memory allocations under heavy VM pressure. Callers provide allocation and free callbacks, and the pool maintains a minimum reserve of reusable elements.

## Core Data Model

A `struct mempool` contains:

- `min_nr`: target reserve size.
- `curr_nr`: current number of reserved elements.
- `elements`: array of reserved element pointers.
- `alloc` / `free`: caller-provided callbacks.
- `pool_data`: callback-private data.
- `lock`: spinlock protecting reserve state.
- `wait`: waitqueue for sleepers waiting for reserve replenishment.

The implementation also supports zero-minimum pools by keeping storage for at least one element and special wakeup handling.

## Creation and Destruction

Main APIs:

- `mempool_init_node()`
- `mempool_init_noprof()`
- `mempool_create_node_noprof()`
- `mempool_exit()`
- `mempool_destroy()`

Initialization allocates the element array and preallocates `max(1, min_nr)` elements. Destruction drains reserved elements through the configured free callback and releases metadata.

## Allocation Flow

`mempool_alloc_noprof()` first tries the normal allocation callback using adjusted GFP flags that avoid emergency reserves, long retries, and noisy warnings. The first pass also suppresses direct reclaim and IO. If that fails, it attempts to remove an element from the reserve.

If direct reclaim is allowed and the reserve is empty, allocation waits on the pool waitqueue with periodic timeout so the normal allocator can be retried as pressure changes. Without direct reclaim, allocation can fail.

`mempool_alloc_bulk_noprof()` applies the same model across an array of element slots, first filling through the callback and then dipping into the reserve for missing entries.

`mempool_alloc_preallocated()` only removes an already-reserved element and never sleeps.

## Free and Refill Flow

`mempool_free_bulk()` returns elements to the reserve while `curr_nr < min_nr`, nulling transferred slots from the caller’s array. Elements beyond the needed reserve remain for the caller to free normally.

`mempool_free()` returns one element to the reserve if needed, otherwise calls the configured free callback.

Memory barriers pair allocation and free paths so a free racing through externally published pointers observes reserve state from after the corresponding allocation. Waiters are woken when elements are added.

## Resizing

`mempool_resize()` can shrink or grow a pool while concurrent allocation/free operations continue. Shrinking frees extra reserved elements. Growing replaces the element pointer array, updates `min_nr`, and opportunistically allocates additional reserve elements; if allocation fails, future frees can refill the pool.

The caller must prevent concurrent destruction.

## Debugging and Sanitizers

The file integrates with:

- fault injection debugfs entries `fail_mempool_alloc` and `fail_mempool_alloc_bulk`;
- SLUB debug poisoning for free/in-use element validation;
- KASAN mempool poison/unpoison helpers;
- kmemleak trace updates when elements are pulled from the reserve.

Debug poisoning supports kmalloc-backed, slab-backed, and page-backed pools, including highmem page mapping where needed.

## Common Callback Helpers

Exported helper alloc/free pairs include:

- `mempool_alloc_slab()` / `mempool_free_slab()`
- `mempool_kmalloc()` / `mempool_kfree()`
- `mempool_alloc_pages()` / `mempool_free_pages()`

These cover slab cache objects, fixed-size kmalloc objects, and page allocations of a configured order.

## Locking and Invariants

`pool->lock` protects `curr_nr` and `elements`. Allocation callbacks are invoked outside the spinlock. The reserve must never exceed `min_nr` except the zero-minimum compatibility slot case. `__GFP_ZERO` is explicitly unsupported for `mempool_alloc_noprof()` because reserve elements are reused and not guaranteed zeroed.
