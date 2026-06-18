# sources/sync-backup/casync/src/canametable.c

## Purpose
`canametable.c` implements `CaNameTable`, a compact context object that records filename hashes and archive offsets for directory entries, plus parent directory context. It is used by location/archive metadata to reconstruct where entries were serialized and to support deterministic lookup structures.

## Important APIs, Types, and Functions
`ca_name_table_new_size()` allocates a flexible-array table with at least `START_ITEMS`. `ca_name_table_ref()` and `ca_name_table_unref()` manage ownership, including parent tables and cached formatted strings. `ca_name_table_make_writable()` implements copy-on-write and growth. `ca_name_table_add()` appends an item and invalidates the cached formatted representation. `ca_name_table_format_realloc_buffer()` and `ca_name_table_format()` serialize a table chain as `O<entry_offset>H<hash>S<start>X<end>...`. `ca_name_table_parse()` and `parse_one()` parse that representation recursively. `ca_name_table_make_bst()` sorts items and lays them out with `ca_make_bst()`. `ca_name_table_equal()` compares complete parent chains.

## Control Flow
Writers allocate or copy a table, append `CaNameItem` records, and optionally format the chain for embedding in a `CaLocation`. Parsing reads an `O` entry offset, then consumes zero or more `H/S/X` triples until another `O` begins a parent table or NUL terminates the string. BST conversion copies and sorts items by hash and start offset before placing them into a binary-search-tree array layout.

## State and Persistence
The table is in-memory, reference counted, and mostly immutable once shared. `formatted` caches the serialized string for reuse and is invalidated on append. Persistence is by embedding the formatted text in location strings rather than by a standalone file format.

## Dependencies and Integration Points
The module depends on `camakebst.h`, `realloc-buffer.h`, and utility parsing/allocation helpers. `calocation.h` includes `canametable.h`, and `test/test-calocation.c` validates name-table formatting and parsing through location round-trips.

## Risks
`ca_name_table_make_writable()` assumes `*t` is non-NULL in some copy paths even though it checks `if (!t)` only; callers currently pass initialized tables. Parsing accepts zero hex digits before numeric conversion, so behavior depends on `safe_atox64()`. Parent recursion can consume deeply nested strings and should be fuzzed. `ca_name_table_make_bst()` does not copy the source parent chain into the new table, which is correct only if callers want a single-level searchable table.

## Test Signals
`test/test-calocation.c` creates parent and child name tables, formats, parses, and checks equality as part of location ID testing. Additional tests should cover parse rejection, copy-on-write with shared references, BST ordering, and cached formatting invalidation after append.
