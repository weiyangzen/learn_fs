# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.h

Defines internal GC interfaces and state.

Key points:
- Declares `gs_gc_reclaim`.
- Defines `struct_shared_procs_s` for shared genus operations: `clear_reloc`, `set_reloc`, and `compact`.
- Defines `gc_state_s` with GC procs, chunk locator, VM spaces, minimum collected space, untraced relocation flag, heap pointer, name table pointer, and debug container chunk.
- Declares ref mark/unmark helpers exported by `igcref.c`.
- Declares allocator validation functions exported by `ilocate.c`.
- Declares `gcst_get_memory_ptr`.
- Defines `print_reloc` debug macro.

Research relevance:
- Primary internal contract tying together Ghostscript’s struct/ref/string compacting GC.
