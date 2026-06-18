# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.h

Declares the C-heap allocator interface. `gs_malloc_memory_t` embeds `gs_memory_common` and tracks the allocation list, configured limit, current used bytes, and max used bytes.

Exports initialization/release routines, default allocator creation/release, wrappers for non-GC `gs_malloc`/`gs_free`, and functions to wrap/unwrap a heap allocator with locking/retry layers. This header is the public entry point for Ghostscript's malloc-backed memory manager.
