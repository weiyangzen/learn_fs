# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.h

Declares internal string GC APIs.

Key points:
- Declares `gc_locate` from `ilocate.c`.
- Declares string GC functions exported by `igcstr.c`:
  - `gc_strings_set_marks`
  - `gc_string_mark`
  - `gc_strings_clear_reloc`
  - `gc_strings_set_reloc`
  - `gc_strings_compact`
  - `igc_reloc_string`
  - `igc_reloc_const_string`
  - `igc_reloc_param_string`

Dependencies and interactions:
- Used by `igc.c` and `igcref.c` through relocation macros/procs.

Research relevance:
- Internal interface between the main object GC and string-specific compaction.
