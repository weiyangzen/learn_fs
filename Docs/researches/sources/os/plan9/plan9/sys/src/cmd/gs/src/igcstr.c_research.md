# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.c

Implements string marking, relocation, and compaction for the Ghostscript GC.

Key points:
- Strings are marked through chunk-level bitmaps (`smark`).
- `gc_strings_set_marks` clears or fills string marks for a chunk.
- `gc_mark_string` marks/unmarks a known-chunk byte range word-at-a-time, with byte-order handling.
- `gc_string_mark` locates a string’s chunk and applies marking, with debug validation for ranges.
- `gc_strings_clear_reloc` prepares relocation metadata by marking all strings and computing relocation.
- `gc_strings_set_reloc` computes relocation offsets per `string_data_quantum` using a zero-bit count table.
- `igc_reloc_string` relocates mutable strings using `sreloc` and `smark`.
- `igc_reloc_const_string` and `igc_reloc_param_string` adapt relocation for const and parameter strings; parameter strings are relocated only when non-persistent.
- `gc_strings_compact` compacts marked string bytes downward from the top of the chunk and fills reclaimed memory.

Research relevance:
- Specialized string allocator compaction layer for the interpreter’s mixed object/string chunks.
