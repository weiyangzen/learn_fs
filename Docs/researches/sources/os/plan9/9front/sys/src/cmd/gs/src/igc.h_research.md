# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.h

Defines internal GC interfaces and state.

Key points:
- Declares `gs_gc_reclaim`.
- Defines `struct_shared_procs_s`, the per-genus operations:
  - `clear_reloc`
  - `set_reloc`
  - `compact`
- Defines `gc_state_s` with:
  - GC procedure vector
  - chunk locator
  - VM spaces
  - minimum collected space
  - untraced relocation flag
  - heap pointer
  - name table pointer
  - debug container chunk
- Declares ref mark/unmark helpers exported by `igcref.c`.
- Declares allocator validation functions exported by `ilocate.c`.
- Declares `gcst_get_memory_ptr` exported by `igc.c`.
- Defines `print_reloc` debug macro.

Dependencies and interactions:
- Included by `igc.c`, `igcref.c`, `igcstr.c`, and `ilocate.c`.
- Ties together struct/ref/string GC mechanisms.

Research relevance:
- Primary internal contract for Ghostscript’s compacting garbage collector.
