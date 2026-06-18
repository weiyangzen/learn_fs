# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.c

Implements Ghostscript’s default C heap allocator and wrapper construction.

Key behavior:
- Defines `gs_malloc_memory_procs`, a full `gs_memory_t` procedure table backed by `malloc`, `free`, and `gs_realloc`.
- Each allocation receives a `gs_malloc_block_t` header containing linked-list pointers, size, structure type, and client name.
- Allocated blocks are tracked in a doubly linked list so `free_all` can release remaining allocations.
- `gs_heap_alloc_bytes` enforces allocator limit accounting, attaches headers, fills debug patterns, and updates current/max used bytes.
- Struct and array allocators record the appropriate Ghostscript type descriptor.
- `gs_heap_resize_object` uses `gs_realloc`, preserves list links, updates size/accounting, and fills newly allocated space under debug fill settings.
- `gs_heap_free_object` finalizes typed objects before unlink/free, reports missing blocks, and tolerates null pointers.
- Root registration APIs are no-ops for this non-GC heap allocator.
- `gs_heap_status` estimates available memory by probing with temporary mallocs.
- `gs_heap_enable_free` can swap real free functions for no-op frees.
- `gs_malloc_wrap` builds a locked wrapper, then a retrying wrapper, around the heap allocator.
- `gs_malloc_init` creates the default allocator, initializes or inherits library context, wraps it, and marks stable memory.
- `gs_malloc_release` unwraps and frees all heap allocator data.

Dependencies:
- Uses `gsmemory.h`, `gsmdebug.h`, `gsstruct.h`, `gsmemlok.h`, and `gsmemret.h`.

Research notes:
- This allocator is both a raw allocator and object allocator.
- The wrapper stack is important: normal clients receive retrying-over-locked-over-malloc memory.
