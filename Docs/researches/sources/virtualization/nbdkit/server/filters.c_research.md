# File Research: sources/virtualization/nbdkit/server/filters.c

Purpose: Adapts a loaded `struct nbdkit_filter` into the internal `struct backend` vtable and handles filter chaining.

Structure:
- `struct backend_filter` embeds `struct backend` plus a copied `struct nbdkit_filter`.
- `filter_register` initializes the backend, calls `filter_init`, checks filter API/version compatibility against the current nbdkit build, copies the filter struct, and runs backend load.

Chain behavior:
- Most callbacks either call the filter callback with a next-function/context or pass straight through to `b->next`.
- `filter_free` frees the entire underlying chain, unloads the filter, and frees its wrapper.
- `plugin_name` and `plugin_magic_config_key` intentionally pass through to the final plugin.

Lifecycle callbacks:
- Handles usage/version/dump fields, config/config_complete, get_ready, after_fork, cleanup, preconnect, list_exports, default_export, open, prepare, finalize, close.
- `next_open` opens the next backend context and stores it in the current filter context.
- `filter_open` supports filters that explicitly call `next_open`, or default-open the next layer when no `.open` is supplied.

Data path:
- Capability and operation callbacks cover export description, size, block size, write/flush/trim/zero/extents/FUA/multi-conn/cache support, and pread/pwrite/flush/trim/zero/extents/cache.
- Missing filter callbacks transparently delegate to the next backend.
- Errors propagate through the internal backend convention using `int *err` on data operations.

Public helper exports:
- `nbdkit_context_get_backend`
- `nbdkit_next_context_open`
- `nbdkit_next_context_close`
- `nbdkit_context_set_next`

Important constraint:
- Filters have strict ABI/API coupling to the exact current nbdkit version via `_api_version` and `_version`; unlike plugins, they are not treated as long-term ABI-stable.
