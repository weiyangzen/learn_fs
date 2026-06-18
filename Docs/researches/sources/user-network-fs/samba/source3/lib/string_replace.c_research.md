## sources/user-network-fs/samba/source3/lib/string_replace.c

Purpose: character mapping helper used by VFS filename translation, notably CATIA/macOS private-use mappings. It builds sparse Unicode mapping tables and applies them to UCS-2 converted filenames in either Unix-to-Windows or Windows-to-Unix direction.

Important types and functions: private `struct char_mappings` stores a 255-entry table with two direction slots, indexed by `enum vfs_translate_direction`. `string_replace_init_map` parses mapping strings of the form `0xNN:0xNN`, `string_replace_allocate` converts an input name to UCS-2, applies mapped code points, and converts back. `macos_string_replace_map` provides the standard control/reserved character mapping into U+F001 and nearby private-use values.

Control flow: initialization allocates a `MAP_NUM` array of table pointers. For each mapping string it parses Unix and Windows values with `strtol`, lazily allocates tables for the ranges containing those code points, initializes identity mappings, and then sets both forward and reverse slots. Allocation converts `name_in` with `push_ucs2_talloc`, iterates each UCS-2 code unit, skips unmapped ranges, substitutes mapped entries in the requested direction, then returns a newly allocated Unix string with `pull_ucs2_talloc`.

State and persistence: mapping tables are talloc-owned by the caller’s context; there is no global mutable state except the exported constant string. Dependencies include Samba charset conversion, talloc, VFS direction enums, and debug logging.

Risks: `MAP_SIZE` is `0xFF`, so range math is unusual and should be treated carefully at boundaries. `errno` is not cleared before `strtol`, making invalid mapping detection weak. The `connection_struct *conn` parameter is unused. Tests should cover bidirectional mapping, unmapped identity behavior, malformed map entries, high code points near range boundaries, and conversion failure propagation.
