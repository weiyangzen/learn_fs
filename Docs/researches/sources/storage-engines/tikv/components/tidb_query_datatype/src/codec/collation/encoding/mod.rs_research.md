# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/mod.rs

## Purpose
Defines the encoding submodule boundary and shared invalid-character formatting for charset conversion errors.

## Important APIs, Types, And Functions
Declares modules `ascii`, `gb18030`, `gb18030_data`, `gbk`, `unicode_letter`, and `utf8`; re-exports all public encoding strategies except the raw data table. `format_invalid_char` returns a quoted preview with ASCII bytes as chars and non-ASCII as hex escapes.

## Control Flow
The formatter preallocates a small string, emits at most the first six bytes before appending ellipsis, then closes the quote. It is used by encoding implementations when constructing `Error::cannot_convert_string`.

## State And Persistence
No runtime state. The module is a compile-time organization point.

## Dependencies And Integration Points
Imports the parent `Encoding` trait, `Error`, `Result`, and byte aliases. Parent `collation/mod.rs` imports these concrete strategies for `match_template_charset!`.

## Risks
The preview loop uses `i > MAX_BYTES_TO_SHOW`, so it can include one byte more than the constant name suggests. Diagnostics are byte-oriented, not character-oriented. This is intentional but can be confusing for multibyte encodings.

## Test Signals
No local tests; indirectly covered by invalid charset conversion tests in concrete encodings.
