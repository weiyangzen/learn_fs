# File Research: sources/os/linux/linux/mm/debug_page_alloc.c

Implements early configuration and guard-page helpers for page allocator debugging.

Key responsibilities:
- Defines `_debug_pagealloc_enabled_early`, initialized from `CONFIG_DEBUG_PAGEALLOC_ENABLE_DEFAULT`, and exports it.
- Defines and exports the `_debug_pagealloc_enabled` static key.
- Defines `_debug_guardpage_enabled` and `_debug_guardpage_minorder`.
- Parses the early `debug_pagealloc=` parameter as a boolean.
- Parses `debug_guardpage_minorder=` and rejects values greater than `MAX_PAGE_ORDER / 2`.
- Implements `__set_page_guard()` and `__clear_page_guard()` for buddy allocator guard pages.

Guard-page behavior:
- `__set_page_guard()` refuses orders greater than or equal to the configured minimum order, marks the page as guard, initializes its buddy list, and stores the order in page private data.
- `__clear_page_guard()` clears the guard flag and zeroes page private data.

Scope:
- This file is small glue around allocator debug flags and guard-page state; the allocator uses these exported/static-key values elsewhere.
