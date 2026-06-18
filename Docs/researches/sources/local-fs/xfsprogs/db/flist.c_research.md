# File Research: sources/local-fs/xfsprogs/db/flist.c

Purpose: parses, expands, and manages field-selection trees used to print or locate structured metadata fields.

Key behavior:
- `flist_make` allocates a field-list node for a name.
- `flist_free` recursively frees children and siblings.
- `flist_scan` parses user-style field paths such as `field.child[0-3].leaf` into an `flist_t` tree.
- `flist_split` tokenizes names, decimal/hex-ish numbers, brackets, dashes, dots, and quoted strings.
- `flist_parse` resolves names against a field table, validates array indices/ranges, computes offsets, expands array ranges into sibling nodes when needed, auto-expands structures when no child is specified, and recursively parses subfields.
- `flist_expand_arrays` replicates child selections for each requested array index.
- `flist_expand_structs` creates child nodes for all non-skipped subfields of a structure.
- `flist_find_ftyp` recursively searches field tables for the first field of a requested type, returning a field-list path.
- `flist_print` dumps internal field-list structure only when `DEBUG_FLIST` is set.

Interactions:
- Used by print commands and by `crc.c` to locate CRC fields.
- Depends on `field.c` helpers, field attributes, debug state, and allocator wrappers.

Risks/notes:
- Parser is intentionally small and supports a limited field path grammar.
- Dynamic field counts/offsets are evaluated against the current object, so corrupt metadata can affect parse results.
