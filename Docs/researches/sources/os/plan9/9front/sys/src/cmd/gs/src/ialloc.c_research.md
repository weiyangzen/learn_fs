# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.c

Implements the interpreter allocator interface over Ghostscript reference memory spaces.

Key behavior:
- `ialloc_init` creates local, stable-local, system, and optionally global/stable-global `gs_ref_memory_t` allocators.
- Level 1 mode aliases global VM to local VM; Level 2 mode creates distinct local/global spaces.
- Initializes VM space tags, optional pointer-stability IDs, GC reclaim hook, and current allocation space.
- Provides accessors for allocator space, new mask, and save level.
- `ialloc_set_space` selects current VM by indexed space.
- `ialloc_reset_requested` clears GC request causes across system/global/local spaces.
- `gs_register_ref_root` registers ref roots with the GC.
- `gs_alloc_ref_array` allocates arrays of `ref` with an extra terminating mark ref for GC relocation metadata; it can extend the current ref run when possible.
- `gs_resize_ref_array` only supports shrinking and handles LIFO shrink specially, otherwise records lost space.
- `gs_free_ref_array` frees only LIFO arrays or large arrays occupying a whole chunk; otherwise nulls references and records lost storage.
- `gs_alloc_string_ref` allocates a byte string and wraps it in a string ref with current space attributes.

Research notes:
- Ref arrays have interpreter-specific GC layout requirements beyond generic heap allocation.
- Much of the code is optimized for stack-like allocation patterns while preserving PostScript save/restore behavior.
