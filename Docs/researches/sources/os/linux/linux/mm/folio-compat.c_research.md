# File Research: sources/os/linux/linux/mm/folio-compat.c

## Purpose

Provides non-inline compatibility wrappers from legacy `struct page` APIs to folio-based implementations. The header comment states callers should eventually be converted to folios, but these functions avoid bloating callers with inline wrappers.

## Exported Compatibility Functions

- `unlock_page(page)` -> `folio_unlock(page_folio(page))`
- `end_page_writeback(page)` -> `folio_end_writeback(page_folio(page))`
- `wait_on_page_writeback(page)` -> `folio_wait_writeback(page_folio(page))`
- `mark_page_accessed(page)` -> `folio_mark_accessed(page_folio(page))`
- `set_page_writeback(page)` -> `folio_start_writeback(page_folio(page))`
- `set_page_dirty(page)` -> `folio_mark_dirty(page_folio(page))`
- `set_page_dirty_lock(page)` -> `folio_mark_dirty_lock(page_folio(page))`
- `clear_page_dirty_for_io(page)` -> `folio_clear_dirty_for_io(page_folio(page))`
- `redirty_page_for_writepage(wbc, page)` -> `folio_redirty_for_writepage(wbc, page_folio(page))`
- `add_to_page_cache_lru(page, mapping, index, gfp)` -> `filemap_add_folio(mapping, page_folio(page), index, gfp)`
- `pagecache_get_page(mapping, index, fgp_flags, gfp)` -> `__filemap_get_folio()` then `folio_file_page()`

## Role in Transition

This file is a shim for subsystems still using `struct page` while the page cache and memory-management internals move toward folio-native APIs. It preserves exported page-based symbols without duplicating logic.

## Error Semantics

`pagecache_get_page()` returns `NULL` when `__filemap_get_folio()` returns an error pointer, matching older page-cache helper behavior rather than propagating encoded errors.
