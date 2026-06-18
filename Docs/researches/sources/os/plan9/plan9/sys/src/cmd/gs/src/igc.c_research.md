# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.c

Implements Ghostscript’s interpreter garbage collector for ref memory.

Key points:
- Defines collector procedure vector `igc_procs` for struct, string, const string, parameter string, ref pointer, and ref-array relocation.
- Defines pointer descriptors for structs, strings, const strings, and refs.
- Main entry point is `gs_gc_reclaim(vm_spaces *pspaces, bool global)`.
- Supports local and global collection, stable allocators, and save levels.
- Registers allocators as roots so change/save lists are traced.
- Clears marks, traces roots, traces non-local chunks during local GC, handles names, refs, arrays, dictionaries, strings, devices, files, fonts, structs, and op arrays.
- Uses a segmented mark stack built from a stack default segment, large free blocks, and heap extensions.
- Handles mark-stack overflow by recording chunk rescan intervals.
- Computes relocation for objects and strings, relocates chunk and root pointers, compacts object/string storage, frees empty chunks, and updates allocator statistics.
- Provides debug phase logging, validation hooks through `ilocate.c`, and relocation printing.
- Exports `gcst_get_memory_ptr`.

Research relevance:
- Core memory-management engine for the Ghostscript interpreter VM: mark, relocate, compact, finalize, and free.
