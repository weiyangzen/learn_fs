# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.c

Implements Ghostscript interpreter name-table lookup, allocation, GC integration, and restore cleanup.

Key points:
- Defines public `name_max_string`.
- Uses generated/permutation data:
  - `hash_permutation`
  - `nt_1char_names`
- Defines structure descriptors for:
  - `name_sub_table`
  - `name_string_sub_table_t`
  - `name_table`
- `names_init`:
  - allocates the name table
  - sets maximum subtable count
  - initializes one-character names as permanent foreign strings
  - reconstructs the free list
- `names_ref`:
  - hashes strings
  - fast-paths empty and one-character names
  - looks up existing names
  - enters new names depending on `enterflag`
  - returns `e_undefined`, `e_limitcheck`, or `e_VMerror` as appropriate
- String/name conversions:
  - `names_string_ref`
  - `names_from_string`
  - `names_enter_string`
- Cache/index helpers:
  - `names_invalidate_value_cache`
  - `names_index`
  - `names_index_ref`
  - `names_index_ptr`
  - `names_next_valid_index`
- GC support:
  - `names_unmark_all`
  - `names_mark_index`
  - `names_ref_sub_table`
  - `names_index_sub_table`
  - `names_index_string_sub_table`
  - `names_trace_finish`
- `names_trace_finish` removes unmarked names from hash chains, clears string data, rebuilds the free list, and may free empty subtables.
- `names_restore` marks only names older than a save and then reuses trace finish cleanup.
- Internal allocation:
  - `name_alloc_sub`
  - `name_free_sub`
  - `name_scan_sub`
- GC descriptors enumerate and relocate subtable pointers and relocate non-foreign name strings.

Dependencies and interactions:
- Used through macros in `iname.h`.
- GC in `igc.c` marks names referenced by refs and operator arrays.
- `igcref.c` relocates name refs by relocating their containing subtable.

Research relevance:
- Core symbol table for PostScript names, tightly coupled to dictionaries, GC, and save/restore.
