# File Research: sources/os/linux/linux/mm/kmsan/shadow.c

## Role

KMSAN shadow/origin metadata address implementation. It maps kernel addresses to metadata, provides dummy metadata for untracked accesses, copies page metadata, handles page allocation/free metadata, maps vmalloc metadata, and installs early page metadata.

## Metadata Storage

- Direct-map pages store metadata page pointers in `struct page` fields:
  - `page->kmsan_shadow`
  - `page->kmsan_origin`
- `shadow_ptr_for()` and `origin_ptr_for()` return page-addressed metadata.
- `page_has_metadata()` requires both shadow and origin pages.
- Metadata pages themselves are marked with no metadata to avoid recursive tracking.
- `dummy_load_page` returns zero metadata for untracked loads.
- `dummy_store_page` absorbs stores to untracked metadata without affecting later loads.

## Address Translation

- `vmalloc_meta()` maps vmalloc and module addresses into parallel shadow/origin virtual ranges:
  - `KMSAN_VMALLOC_SHADOW_START`
  - `KMSAN_VMALLOC_ORIGIN_START`
  - `KMSAN_MODULES_SHADOW_START`
  - `KMSAN_MODULES_ORIGIN_START`
- Origin addresses are aligned down to `KMSAN_ORIGIN_SIZE`.
- `kmsan_get_metadata()` handles vmalloc/module metadata, architecture-specific metadata, and direct-map page metadata.
- Invalid or metadata-less addresses return `NULL`.

## Compiler Metadata Pointer API

- `kmsan_get_shadow_origin_ptr()` returns shadow/origin pointers for instrumented loads/stores.
- If KMSAN is disabled or metadata is absent, it returns dummy metadata:
  - stores go to dummy store page.
  - loads read zero shadow/origin from dummy load page.
- It warns on access sizes larger than a page and verifies metadata contiguity.

## Page Metadata Operations

- `kmsan_copy_page_meta()` copies shadow and origin metadata from one page to another, or unpoisons destination if source lacks metadata.
- `kmsan_alloc_page()` initializes metadata for newly allocated pages:
  - zeroed allocations or disabled KMSAN get clear metadata.
  - nonzero allocations get shadow set to poisoned and origin filled with a saved stack handle.
  - runtime allocations are left alone to avoid recursion.
- `kmsan_free_page()` poisons freed pages with use-after-free origins.
- `kmsan_setup_meta()` assigns contiguous shadow/origin page arrays to a page block.

## Vmap and Early Allocation

- `kmsan_vmap_pages_range_noflush()` maps metadata pages corresponding to physical pages into vmalloc/module metadata ranges and flushes TLB/cache state.
- It builds arrays of source shadow/origin pages, maps both ranges with `PAGE_KERNEL`, and frees temporary arrays.
- `kmsan_init_alloc_meta_for_range()` allocates shadow and origin memory with memblock for boot-time ranges and assigns metadata pages to every covered real page.

## Dependencies

Uses architecture KMSAN hooks, vmalloc/module metadata layout constants, memblock, TLB/cache flushing, slab helpers, page allocator hooks, and KMSAN core origin/poison routines.

## Research Notes

This file defines where KMSAN metadata lives. The fallback dummy pages are essential for tolerating untracked memory, while direct-map page metadata and vmalloc/module parallel ranges provide the main metadata mapping mechanisms.
