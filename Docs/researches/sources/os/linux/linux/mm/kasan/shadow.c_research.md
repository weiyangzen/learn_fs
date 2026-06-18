# File Research: sources/os/linux/linux/mm/kasan/shadow.c

## Role

Runtime shadow-memory management for generic and software tag-based KASAN. It provides instrumented memory access wrappers, poisoning/unpoisoning primitives, memory hotplug shadow allocation, vmalloc/module shadow population, and vmalloc shadow release.

## Key Functions

- `__kasan_check_read()` and `__kasan_check_write()` call `kasan_check_range()` for compiler/runtime checks.
- Optional `memset`, `memmove`, and `memcpy` overrides validate source/destination ranges before calling raw implementations.
- `__asan_memset`, `__asan_memmove`, and `__asan_memcpy` are exported compiler instrumentation entry points; software tag mode aliases HWASan memintrinsics to them.
- `kasan_poison()` writes a poison/tag value over shadow bytes for granule-aligned ranges.
- `kasan_poison_last_granule()` records partial-granule accessibility for generic mode.
- `kasan_unpoison()` unpoisons a rounded-up range with the pointer tag, then applies generic partial-granule poisoning.
- Memory hotplug support maps or frees shadow memory for online/offline memory ranges, leaking boot-time shadow that cannot currently be released.
- `__kasan_populate_vmalloc()` allocates and maps vmalloc/module shadow pages, initializes them to invalid, handles UML’s pre-mapped shadow case, and relies on vmalloc/page-table ordering for visibility.
- `__kasan_release_vmalloc()` frees only shadow pages fully covered by the vmalloc free region, with optional page-table removal and TLB flush.
- `__kasan_unpoison_vmalloc()` assigns a random tag unless told to keep the existing tag, skips executable mappings for software tag mode, and unpoisons the vmalloc range.
- `__kasan_poison_vmalloc()` poisons freed vmalloc shadow as invalid.
- Without `CONFIG_KASAN_VMALLOC`, module shadow allocation/free uses `__vmalloc_node_range()` and tracks `VM_KASAN`.

## Dependencies

Uses KASAN mapping helpers, vmalloc internals, page-table walkers, memory hotplug notifiers, memblock/vmalloc allocation, cache/TLB flush helpers, kmemleak, KFENCE include visibility, and architecture hooks.

## Research Notes

This file owns the actual shadow state that common and mode-specific reporting later interprets. The vmalloc release logic is especially careful: because vmalloc regions and shadow pages are not aligned the same way, it frees only pages proven unused by the surrounding free region and documents the concurrency assumptions around `free_vmap_area_lock`.
