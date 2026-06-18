# sources/storage-engines/sqlite/ext/fts5/fts5_unicode2.c

## Purpose
`fts5_unicode2.c` is a machine-generated Unicode classification and folding support module for FTS5 tokenization. It provides case folding, optional diacritic removal, Unicode general-category parsing, codepoint category lookup, and ASCII token table derivation.

## Important APIs, Types, And Functions
Public functions are `sqlite3Fts5UnicodeIsdiacritic()`, `sqlite3Fts5UnicodeFold()`, `sqlite3Fts5UnicodeCatParse()`, `sqlite3Fts5UnicodeCategory()`, and `sqlite3Fts5UnicodeAscii()`. The private `fts5_remove_diacritic()` maps supported lower-case Latin codepoints with diacritics back to ASCII bases. Large generated arrays encode category ranges and case-fold rules.

## Control Flow
`sqlite3Fts5UnicodeFold()` handles ASCII uppercase quickly, binary-searches BMP folding ranges, applies encoded offsets when range/parity match, then optionally removes diacritics. `sqlite3Fts5UnicodeCategory()` locates a compressed map range by block and binary search, returning a 5-bit category id. `sqlite3Fts5UnicodeCatParse()` turns strings such as `L*` and `Nd` into category masks, and `sqlite3Fts5UnicodeAscii()` derives a 128-byte ASCII token table from the same category data.

## State And Persistence
The module is stateless and read-only. Tables are static data. It does not allocate or mutate state; its results affect tokenizer behavior and therefore the persistent FTS5 index content produced by tokenizers.

## Dependencies And Integration Points
It includes `<assert.h>` and uses SQLite/FTS5 integer typedefs. `fts5_tokenize.c` consumes it for Unicode category checks, folding, diacritic handling, and ASCII table setup.

## Risks
Manual edits to generated tables are high risk. Unicode version drift can affect compatibility. Diacritic removal is not full normalization. Compressed table bounds make off-by-one errors broad in impact.

## Test Signals
Compare folding and category lookup for ASCII, Latin-1, Greek, Cyrillic, combining marks, private-use/category edges, unsupported high codepoints, category strings, and tokenizer-level `unicode61` behavior.
