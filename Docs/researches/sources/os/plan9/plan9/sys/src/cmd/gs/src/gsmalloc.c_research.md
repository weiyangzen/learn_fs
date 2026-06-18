# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.c

Implements a `gs_memory_t` allocator backed directly by C `malloc`/`free`. Each allocation is prefixed with `gs_malloc_block_t`, linked into an allocation list, and records size, type descriptor, and client name. This allows status reporting and bulk cleanup via `free_all`.

Allocation paths support raw bytes, structures, byte arrays, struct arrays, strings, resize, object-size/type lookup, finalization on free, optional debug fill patterns, and enable/disable of free operations. It detects size overflow for byte arrays and logs missing blocks when freeing unknown pointers.

`heap_available` probes the heap with up to 20 temporary 64 KB allocations to estimate available memory for status reporting. `gs_malloc_wrap` layers a monitor-locked wrapper and retrying wrapper around the raw heap allocator; `gs_malloc_unwrap` reverses this. `gs_malloc_init` creates the default wrapped allocator and initializes or inherits the library context.

This is the default non-GC allocator foundation used by Ghostscript in this tree.
