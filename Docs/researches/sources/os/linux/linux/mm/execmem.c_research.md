# File Research: sources/os/linux/linux/mm/execmem.c

## Purpose

Implements the executable memory allocator used for kernel executable regions such as module text and related execmem types. It abstracts architecture-provided executable-memory ranges, fallback ranges, permissions, alignment, and optional read-only-execute cache behavior.

## Global Configuration

- `execmem_info`: selected allocator configuration, set during init.
- `default_execmem_info`: fallback setup using `VMALLOC_START..VMALLOC_END`, `PAGE_KERNEL_EXEC`, alignment 1.
- `execmem_arch_setup()` is weak and may be overridden by architectures.

`execmem_validate()` ensures the default range has alignment, start/end, and pgprot. It also strips unsupported `EXECMEM_ROX_CACHE` flags if the architecture lacks `CONFIG_ARCH_HAS_EXECMEM_ROX`.

`execmem_init_missing()` fills unspecified execmem ranges from `EXECMEM_DEFAULT`, except `EXECMEM_MODULE_DATA`, which receives `PAGE_KERNEL`.

## Allocation Without ROX Cache

Under `CONFIG_MMU`, `execmem_vmalloc()` allocates from the selected primary range using `__vmalloc_node_range()`, then retries the fallback range if configured. It adds KASAN shadow handling when `EXECMEM_KASAN_SHADOW` is set.

Without MMU, it falls back to `vmalloc()`.

`execmem_vmap()` reserves virtual memory for `EXECMEM_MODULE_DATA` using the configured range and fallback.

## ROX Cache Path

When `CONFIG_ARCH_HAS_EXECMEM_ROX` is enabled, the file provides an executable-memory cache that keeps memory mapped ROX and temporarily flips regions writable for updates.

Key structures:

- `struct execmem_cache`
  - `mutex`
  - `busy_areas` maple tree
  - `free_areas` maple tree
  - `pending_free_cnt`

Important constants:

- `FREE_DELAY`: delayed retry for slow frees.
- `PENDING_FREE_MASK`: marks busy-tree entries pending async free.

Main ROX cache behavior:

- `execmem_cache_populate_alloc()` allocates PMD-rounded memory when possible, fills it with trapping instructions, marks it ROX, adds it to the free tree, then allocates the requested range.
- `execmem_cache_alloc_locked()` finds a suitable free range in primary or fallback execmem range, moves the allocated part to `busy_areas`, and leaves any remainder in `free_areas`.
- `__execmem_cache_free()` forces memory RW/NX, fills trapping instructions, restores ROX, moves range back to free tree, and removes it from busy tree.
- `execmem_cache_free()` tries a non-retry GFP path under lock; on failure marks the entry pending and schedules delayed work.
- `execmem_cache_free_slow()` retries pending frees with `GFP_KERNEL`.
- `execmem_cache_clean()` eventually releases PMD-aligned free cached areas back to vmalloc and restores direct-map validity.

## Permissions

- `execmem_force_rw()` converts allocated executable memory to writable and NX.
- `execmem_restore_rox()` restores read-only executable permissions.
- `execmem_set_direct_map_valid()` toggles direct-map validity for vmalloc backing pages and rolls back on failure.

When ROX cache is not enabled, permission forcing is a no-op and the cache allocator/free path returns unused.

## Public Interfaces

- `execmem_alloc(type, size)`: page-aligns size and allocates from cache or vmalloc range.
- `execmem_alloc_rw(type, size)`: allocates, then forces writable permissions, returning NULL if permission change fails.
- `execmem_free(ptr)`: warns on interrupt context, frees through ROX cache if recognized, otherwise `vfree()`.
- `execmem_is_rox(type)`: reports whether the type uses ROX cache.
- `execmem_vmap(size)`: returns a `vm_struct` for module data range under MMU.

## Initialization

- If `CONFIG_ARCH_WANTS_EXECMEM_LATE`, initialization is registered with `core_initcall(execmem_late_init)`.
- Otherwise, `execmem_init()` directly initializes execmem configuration.

## Notable Invariants

- Requested allocation sizes are page-aligned.
- ROX cache free/alloc state is tracked with maple-tree address ranges.
- New executable cache memory is filled with trapping instructions before being exposed.
- `execmem_free()` must not be called from interrupt context because freeing RO memory via vmalloc is unsupported there.
