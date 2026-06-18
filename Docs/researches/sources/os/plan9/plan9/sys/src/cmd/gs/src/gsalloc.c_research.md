# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.c

Purpose: Implements Ghostscript’s standard reference-aware memory allocator, including object/string allocation, freelists, chunk management, GC status integration, roots, and debug dumping.

Key interfaces: `gs_ref_memory_procs`, `ialloc_alloc_state`, `ialloc_add_chunk`, `ialloc_gc_prepare`, `ialloc_reset`, `ialloc_reset_free`, `ialloc_set_limit`, `ialloc_consolidate_free`, chunk helpers (`alloc_link_chunk`, `alloc_init_chunk`, `alloc_close_chunk`, `alloc_open_chunk`, `alloc_unlink_chunk`, `alloc_free_chunk`, `chunk_locate_ptr`), and debug helpers under `DEBUG`.

Control flow: allocator state is allocated as a solo object with a manually built header. Small objects use size-class freelists, large free objects use a large freelist, normal objects allocate upward from chunk bottom, and strings allocate downward from chunk top. Large or immovable allocations get dedicated chunks. Freeing finalizes objects, reclaims LIFO top objects, puts reusable objects on freelists, frees dedicated chunks when possible, or accounts lost space. Consolidation scans chunks for adjacent free objects and whole-free chunks. GC status computes limits from `max_vm`, `vm_threshold`, previous status, and signal fields.

Dependencies: Deeply tied to Ghostscript GC/structure descriptors (`gsstruct.h`, `gxalloc.h`), raw memory, stream lists, save/restore state, object headers, string mark/relocation tables, and debug infrastructure.

Risks and notes: This is allocator core code with many pointer and size invariants. Controlled-memory behavior differs from normal GC memory. Some debug paths return instead of aborting on allocator corruption. Integer overflow checks exist in key places but callers and structure descriptors must still provide sane sizes.
