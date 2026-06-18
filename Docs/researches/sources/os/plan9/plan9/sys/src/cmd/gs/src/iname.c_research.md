# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.c

Implements Ghostscript interpreter name-table lookup, allocation, GC integration, and restore cleanup.

Key points:
- Defines public `name_max_string`.
- Uses generated/permutation data: `hash_permutation` and `nt_1char_names`.
- Defines structure descriptors for `name_sub_table`, `name_string_sub_table_t`, and `name_table`.
- `names_init` allocates the table, sets maximum subtable count, initializes one-character names as permanent foreign strings, and reconstructs the free list.
- `names_ref` hashes strings, fast-paths empty and one-character names, looks up existing names, enters new names depending on `enterflag`, and returns `e_undefined`, `e_limitcheck`, or `e_VMerror` as appropriate.
- Implements string/name conversions, cache/index helpers, and name iteration.
- GC support includes unmarking, marking by index, subtable lookup, string-subtable lookup, and trace finish.
- `names_trace_finish` removes unmarked names from hash chains, clears string data, rebuilds the free list, and may free empty subtables.
- `names_restore` marks only names older than a save and reuses trace-finish cleanup.
- GC descriptors enumerate and relocate subtable pointers and non-foreign name strings.

Research relevance:
- Core PostScript symbol table, tightly coupled to dictionaries, GC, and save/restore.
