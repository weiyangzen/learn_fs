# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.c

Purpose: Standard Ghostscript GC-aware reference memory allocator.

Allocator state: Defines structure descriptors for `gs_ref_memory_t` and chunks, allocator procedure tables, GC status accessors, stable-memory access, root registration, and initialization via `ialloc_alloc_state`. `ialloc_solo` creates allocator/chunk storage outside the GC-managed object space while still giving it a GC-visible object header.

Allocation model: Uses chunks with object allocation growing upward from `cbot` and string allocation growing downward from `ctop`. Small objects use size-indexed freelists, large objects use a large freelist or one-object chunks, and strings can get dedicated chunks. Controlled allocators can accept externally supplied chunks and disable further acquisition.

Free/resize/consolidation: `i_free_object` finalizes objects, performs LIFO rollback when possible, frees one-object chunks, or links reusable blocks to freelists. `i_resize_object` and `i_resize_string` attempt in-place growth/shrink before allocating replacements. `ialloc_consolidate_free`, `consolidate_chunk_free`, `remove_range_from_freelist`, `trim_obj`, and `scavenge_low_free` reclaim contiguous free ranges.

Chunk management: `alloc_acquire_chunk` enforces GC/max-VM thresholds, can signal the GC, allocates raw chunk metadata/data from non-GC memory, initializes string marking/relocation tables, and links chunks in address order. `alloc_close_chunk` and `alloc_open_chunk` synchronize cached current-chunk state; `alloc_free_chunk` releases chunk data and metadata.

GC/debug support: `ialloc_gc_prepare` unlinks streams before collection. Debug builds include object/chunk/memory dump utilities and pointer-finding helpers. Allocation tracing marks space, movable/immovable state, operation kind, allocation type, and source path such as freelist, LIFO, large chunk, or lost space.

Dependencies and notes: Central to Ghostscript memory semantics and save/restore/GC interaction. Key invariants are chunk ordering, object headers preceding user pointers, accurate freelist membership, and respecting older save levels.
