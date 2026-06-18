# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalloc.h

Purpose: Defines internal structures and macros for Ghostscript’s standard reference-aware allocator and chunk management.

Key definitions:
- `chunk_t` describes a memory chunk with bottom-up aligned object allocation and top-down string allocation.
- String GC constants and macros: `string_data_quantum`, `string_space_quantum`, `string_chunk_space()`, `STRING_FREELIST_SPACE()`.
- Chunk scanning macros: `SCAN_CHUNK_OBJECTS`, `DO_ALL`, `END_OBJECTS_SCAN`.
- Pointer-location macros and `chunk_locator_t`.
- `gs_ref_memory_t` extends `gs_memory_t` with chunk chain, freelists, save/restore state, GC roots, allocation accounting, stream/name pointers, and debug counters.
- Debug dump controls under `DEBUG`.

Declared functions:
- Chunk lifecycle: `alloc_init_chunk()`, `alloc_close_chunk()`, `alloc_open_chunk()`, `alloc_link_chunk()`, `alloc_unlink_chunk()`, `alloc_free_chunk()`.
- String free-list init: `alloc_init_free_strings()`.
- Pointer lookup: `chunk_locate_ptr()`.
- Debug printing/dumping APIs.

Behavior:
- Chunks may be nested for PostScript save/restore.
- Refs are grouped into `st_refs` objects with bounds to aid GC relocation scanning.
- String metadata includes mark and relocation tables stored near the top of chunks.
- Small and large free blocks are tracked with multiple freelists.

Dependencies:
- Requires `gsmemory.h`, `gsstruct.h`, `gsalloc.h`, `gxobj.h`, architecture alignment constants, and interpreter `ref`/`stream` forward declarations.

Notable risks:
- This header exposes allocator internals to save/restore and GC code; layout changes affect memory management correctness.
- Many macros assume object-header layout and alignment invariants.
