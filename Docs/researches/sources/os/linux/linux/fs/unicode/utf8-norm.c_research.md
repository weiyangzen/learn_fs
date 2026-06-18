# File Research: sources/os/linux/linux/fs/unicode/utf8-norm.c

## Purpose
Implements the runtime UTF-8 trie interpreter and normalization cursor used by Linux filesystem Unicode validation, NFDI normalization, and NFDICF casefolding.

## Main Contents
- `utf8version_is_supported()`: checks whether a requested packed Unicode version appears in the generated age table.
- UTF-8 helpers:
  - `utf8clen()` returns sequence byte length from a valid leading byte.
  - `utf8decode3()` and `utf8encode3()` support Hangul decomposition.
- Trie format definitions:
  - Internal node bit flags: `BITNUM`, `NEXTBYTE`, `OFFLEN`, `RIGHTPATH`, `TRIENODE`, `RIGHTNODE`, `LEFTNODE`.
  - Leaf accessors: generation, canonical combining class, decomposition string.
- Hangul support:
  - Constants for Unicode Hangul decomposition.
  - `utf8hangul()` synthesizes a decomposition leaf for Hangul syllables.
- Trie lookup:
  - `utf8nlookup()` traverses the generated compact trie with a byte limit and returns a leaf only for valid UTF-8 Unicode sequences.
  - `utf8lookup()` is the unbounded wrapper.
- Length and cursor APIs:
  - `utf8nlen()` returns normalized byte length or `-1` for invalid UTF-8.
  - `utf8ncursor()` initializes a bounded normalization cursor.
  - `utf8byte()` emits one byte at a time from the normalized stream, handling decomposition, default-ignorable empty mappings, version gating, and canonical combining class order.
- KUnit module exports are enabled when normalization tests are modular.

## Important Design Points
- Trie lookup doubles as validation: failure to find a leaf means invalid/non-Unicode UTF-8 input.
- Code points newer than the selected Unicode version are treated as undecomposed stoppers.
- Decomposition strings are emitted through cursor state without decrementing the original input length.
- Canonical combining class ordering is implemented by repeated scans between stoppers, emitting classes in ascending order.
- Empty decompositions are used for default-ignorable code points and can reduce normalized length to zero.
- Hangul decompositions are generated at runtime from a compact marker rather than stored fully in the table.

## Cross-File Relationships
- Includes `utf8n.h` for cursor/table declarations.
- Consumes generated trie data from `utf8_data_table`.
- Called by public APIs in `utf8-core.c`.
- Shares trie layout constants and assumptions with `mkutf8data.c`.

## Risks / Review Notes
- `utf8byte()` is stateful and subtle; cursor fields `s`, `p`, `ss`, `sp`, `ccc`, and `nccc` must remain consistent.
- The lookup code assumes generated trie offsets and markers are valid; corrupt generated data would cause bad traversal.
- Bounded cursors reject strings starting with continuation bytes but rely on trie lookup for deeper UTF-8 validation.
