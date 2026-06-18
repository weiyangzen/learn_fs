# File Research: sources/os/linux/linux/mm/zpdesc.h

## Purpose

`zpdesc.h` defines `struct zpdesc`, the zsmalloc-specific descriptor overlay for pages that back zsmalloc pool memory. It is a transitional abstraction over `struct page`/`struct folio` fields used by zsmalloc while letting zsmalloc code express its own metadata model directly.

## Data Layout

`struct zpdesc` overlays selected `struct page` fields and must not grow beyond `struct page`. Static assertions verify field offsets:

- `flags` overlays page flags.
- `lru` is indirectly used by page migration.
- `movable_ops` overlays `mapping` for movable-page operations.
- `next` and `handle` overlay `__folio_index`; `next` links component pages in normal zspages, while `handle` stores the allocation handle for huge zspages.
- `zspage` overlays `private` and points to the owning zspage metadata.
- `first_obj_offset` overlays `page_type`; lower 24 bits hold the first object offset and upper bits reserve the zsmalloc page type.
- `_refcount` overlays the page reference count.

Documented page flags:

- `PG_private` identifies the first component page of a zspage.
- `PG_locked` is used by page migration.

## Conversion Helpers

The header provides type-generic conversion helpers:

- `zpdesc_page()` converts a zpdesc to the first underlying `struct page`.
- `zpdesc_folio()` converts to the backing folio.
- `page_zpdesc()` converts a known head or order-0 page into a zpdesc.
- `pfn_zpdesc()` and `zpdesc_pfn()` bridge PFNs and descriptors.

The conversion macros are explicit because the representation may change as zsmalloc continues moving away from raw `struct page` assumptions.

## Operations

Inline wrappers expose folio/page operations in zpdesc terms:

- Locking: `zpdesc_lock()`, `zpdesc_trylock()`, `zpdesc_unlock()`, `zpdesc_wait_locked()`, `zpdesc_is_locked()`
- Lifetime: `zpdesc_get()`, `zpdesc_put()`
- Mapping: `kmap_local_zpdesc()`
- Page type and migration setup: `__zpdesc_set_movable()`, `__zpdesc_set_zsmalloc()`
- Zone lookup: `zpdesc_zone()`

## Integration Points

`zsmalloc.c` uses this header for all zspage component-page operations: allocation, free, chain construction, object copy, migration, compaction, page-state accounting, and highmem mapping. The header also interfaces with generic migration through `SetPageMovableOps()` and with zsmalloc page typing through `__SetPageZsmalloc()`.

## Invariants And Risks

The central invariant is that `struct zpdesc` must exactly match the `struct page` fields zsmalloc overlays. Changing `struct page`, folio internals, or zsmalloc metadata without updating these static assertions can corrupt unrelated page metadata. The 24-bit `first_obj_offset` field limits direct offset representation to pages up to 16 MiB. Callers must use helpers rather than accessing overlay fields through casts or direct `struct page` internals.

Test focus should include build-time assertions across architecture page models, zsmalloc allocation/free, page migration, highmem mapping, and large `PAGE_SIZE` configurations.
