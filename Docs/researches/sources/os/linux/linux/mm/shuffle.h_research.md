# File Research: sources/os/linux/linux/mm/shuffle.h

Internal header for page allocator freelist shuffling. It exposes the static-key-gated entry points used by page allocator initialization and free paths.

Key responsibilities:
- Defines `SHUFFLE_ORDER` as `MAX_PAGE_ORDER`.
- Declares `page_alloc_shuffle_key`, `__shuffle_free_memory()`, `__shuffle_zone()`, and `shuffle_pick_tail()` when shuffling is configured.
- Provides inline wrappers `shuffle_free_memory()` and `shuffle_zone()` that return immediately unless the static branch is enabled.
- Provides `is_shuffle_order()` so allocator code can cheaply test whether an order participates in shuffle-related behavior.
- Provides no-op fallbacks when `CONFIG_SHUFFLE_PAGE_ALLOCATOR` is disabled.

Important behavior:
- The static branch keeps the disabled fast path cheap even in builds that include shuffling support.
- Disabled or unconfigured builds always return `false` for `shuffle_pick_tail()` and `is_shuffle_order()`.

Dependencies:
- Depends on jump labels/static keys and page allocator types such as `pg_data_t` and `struct zone` supplied by including contexts.

Notable risks:
- The wrappers intentionally hide all implementation details behind the static branch; callers must use the header helpers rather than call underscored functions directly if they need the disabled fast path.
