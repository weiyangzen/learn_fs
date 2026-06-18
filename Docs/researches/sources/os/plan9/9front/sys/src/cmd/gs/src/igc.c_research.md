# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.c

Implements Ghostscript’s interpreter garbage collector for ref memory.

Key points:
- Defines the collector procedure vector `igc_procs`, including relocation for structs, strings, const strings, parameter strings, refs, and ref arrays.
- Defines pointer descriptors:
  - `ptr_struct_procs`
  - `ptr_string_procs`
  - `ptr_const_string_procs`
  - `ptr_ref_procs`
- Main entry point is `gs_gc_reclaim(vm_spaces *pspaces, bool global)`.
- Supports local and global collection:
  - Determines which VM spaces to trace and which to compact.
  - Handles stable allocators and save levels.
  - Registers allocator roots so change/save lists are traced.
- Marking:
  - Clears object and string marks in collected spaces.
  - Unmarks roots and optionally names.
  - Builds a mark stack from a default C-stack segment, free blocks, and heap-allocated extensions.
  - Traces roots, non-local chunks during local GC, names, refs, arrays, dictionaries, strings, devices, files, fonts, structs, and op arrays.
  - Handles mark-stack overflow by recording rescan intervals in chunks.
- Relocation/compaction:
  - Clears reloc info for traced-only chunks.
  - Disables freeing while finalizers run.
  - Computes object/string relocation.
  - Relocates pointers in chunks and roots.
  - Compacts object and string storage.
  - Frees empty chunks.
  - Updates allocator saved-state memory statistics.
- Debug support:
  - Phase logging under debug flags.
  - Pointer validation hooks through `ilocate.c`.
  - Relocation printing via `print_reloc_proc`.
- Exports `gcst_get_memory_ptr`.

Dependencies and interactions:
- Calls string GC helpers from `igcstr.c`.
- Calls ref GC helpers from `igcref.c`.
- Uses name-table marking and trace finish routines.
- Uses `ilocate.c` for chunk lookup and validation.
- Uses operator-array name tables from `opdef.h`.

Risks and notes:
- Relocation uses compacting GC assumptions and low-level pointer arithmetic.
- Debug paths can abort on impossible states.
- Comments note deprecated const-removal puns in relocation.

Research relevance:
- This is the core memory-management engine for the Ghostscript interpreter VM: mark, relocate, compact, finalize, and free.
