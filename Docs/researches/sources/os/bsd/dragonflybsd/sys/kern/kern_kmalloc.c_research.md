# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_kmalloc.c

## Purpose

`kern_kmalloc.c` implements DragonFlyBSD's type-stable `kmalloc_obj` allocator for fixed-size object zones. It uses `struct malloc_type` plus `struct kmalloc_mgt` state to provide per-type slab allocation, with slab memory returned cleanly when a zone is destroyed.

## Main Responsibilities

- Initializes and tears down per-type object allocation management with `malloc_mgt_init()` and `malloc_mgt_uninit()`.
- Allocates and frees fixed-size objects through `_kmalloc_obj()` and `_kfree_obj()`.
- Maintains per-CPU active and alternate slabs for fast allocation.
- Maintains per-type global partial, full, and empty slab lists.
- Maintains a per-CPU global free-slab cache to reduce kernel map churn.
- Retires fully free slabs gradually through `malloc_mgt_poll()`.
- Optionally checks double frees with a per-slab bitmap under `KMALLOC_CHECK_DOUBLE_FREE`.

## Core Data Model

Each slab is `KMALLOC_SLAB_SIZE` aligned and contains metadata plus a free-object ring in `fobjs[]`. The allocator tracks `aindex` for allocation consumption, `findex` for free-slot reservation, and `xindex` as a synchronizer showing the free-side object pointer has been stored. A slab's `type`, original CPU, object size, object count, object offset, magic, spinlock, and EXIS state describe its lifetime and safety status.

Each malloc type has per-CPU `ks_use[]` state with local `active` and `alternate` slabs. The type-wide `ks_mgt` holds shared `partial`, `full`, and `empty` lists plus counters. Fully free slabs can move into `gd_kmslab` per-CPU free-slab caches, while overflow is returned to `kmem_slab_free()`.

## Allocation Flow

`_kmalloc_obj()` first enforces the type limit using loose per-CPU memory accounting. It then enters a critical section and tries the current CPU's active slab, then alternate slab. If both are unavailable, it rotates a partial or full slab from the type-wide manager into the per-CPU active slot, sending the displaced alternate slab to the type empty list. If no existing slab has objects, it polls empty slabs and finally obtains a new slab from the CPU slab cache or `kmem_slab_alloc()`.

New slabs are zeroed as metadata, populated with fixed-size object addresses, marked with `KMALLOC_SLAB_MAGIC`, and rotated into the active slot. On success, per-CPU allocation counters and loose memory counters are updated, and `M_ZERO` is honored if requested.

## Free and Retirement Behavior

`_kfree_obj()` derives the owning slab by masking the object pointer, verifies the slab magic and that it is not already fully free, updates current-CPU statistics, reserves a free slot by atomically incrementing `findex`, stores the freed object in the ring, then increments `xindex` to complete publication.

Freed objects do not immediately move their slab between manager lists. Empty-list polling later classifies slabs as partial or full. `malloc_mgt_poll()` periodically moves fully free slabs from the full list into a retirement list when `xindex == findex` and `exis_freeable()` says the type-stability delay has elapsed. It caches as many retired slabs as possible and frees the rest.

## Concurrency Notes

Per-CPU active/alternate slabs are manipulated under a critical section on the local CPU. Type-wide slab lists are protected by `kmalloc_mgt.spin`. Global free-slab cache transfer uses atomic pointer swaps and compare/exchange, with `remote_free_slabs` only manipulated atomically. Free-side publication intentionally separates `findex` reservation from the object store and `xindex` synchronization.
