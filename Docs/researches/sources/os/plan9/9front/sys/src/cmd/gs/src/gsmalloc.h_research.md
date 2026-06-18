# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.h

Client interface for the default C heap allocator.

Key declarations:
- `gs_malloc_memory_t` embeds `gs_memory_common` and tracks allocated list, limit, used bytes, and max used bytes.
- `gs_malloc_memory_init`
- `gs_malloc_memory_release` macro using `gs_memory_free_all(... FREE_ALL_EVERYTHING ...)`
- `gs_malloc_init`
- `gs_malloc_release`
- `gs_malloc` and `gs_free` macros allocate through `mem->non_gc_memory`.
- Wrapper helpers: `gs_malloc_wrap`, `gs_malloc_wrapped_contents`, and `gs_malloc_unwrap`.

Research notes:
- Requires `gsmemory.h`.
- Public API exposes both raw heap memory manager construction and the wrapped allocator used by clients.
