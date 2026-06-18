# File Research: sources/os/linux/linux/mm/kasan/common.c

Common KASAN runtime code shared across modes.

Main responsibilities:
- Defines/export runtime enabled static key for deferred or hardware-tag modes.
- Saves stack traces and allocation/free tracks.
- Enables/disables per-task KASAN depth for generic/software-tag modes.
- Poisons/unpoisons page, slab, kmalloc, large kmalloc, mempool, stack, and vmalloc ranges.
- Assigns tags for tag-based modes while preserving stable tags for constructor or `SLAB_TYPESAFE_BY_RCU` caches.
- Validates invalid free and double free by checking object alignment and accessibility.
- Integrates with quarantine for generic mode and skips KFENCE addresses.

Important paths:
- `__kasan_unpoison_pages()` assigns a random tag, unpoisons page memory, and records page tags unless highmem or sampled out.
- `__kasan_slab_alloc()` assigns object tags and unpoisons slab objects.
- `__kasan_slab_free()` poisons freed objects, records free metadata, and optionally quarantines.
- `__kasan_kmalloc()` and `__kasan_kmalloc_large()` poison precise redzones.
- `__kasan_krealloc()` unpoisons new accessible size and re-poisons kmalloc redzones.
- `__kasan_unpoison_vmap_areas()` gives multi-area vmalloc allocations a shared tag.

Correctness notes:
KASAN avoids touching KFENCE allocations, uses mode-specific precision, and treats `still_accessible` RCU frees specially to avoid hiding `SLAB_TYPESAFE_BY_RCU` misuse.
