# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/ascii.rs

## Purpose
Defines decoding behavior for binary and ASCII charsets. Binary is a pass-through; ASCII validates every byte.

## Important APIs, Types, And Functions
`EncodingBinary` implements `Encoding::decode` by cloning the input bytes. `EncodingAscii` implements `decode` by checking `u8::is_ascii` for every byte and returning `Error::cannot_convert_string` on the first non-ASCII byte.

## Control Flow
Binary decoding immediately returns `Bytes::from(data)`. ASCII decoding scans the full slice; if all bytes are ASCII it returns the original bytes, otherwise it formats a short escaped invalid-string preview through `format_invalid_char` and fails.

## State And Persistence
No state is stored. Both encoding structs are zero-sized strategy types.

## Dependencies And Integration Points
Depends on the shared `Encoding` trait and shared error formatter in `encoding/mod.rs`. It is exposed through `pub use ascii::*` and selected by `match_template_charset!` for `Binary` and `Ascii`.

## Risks
The failure message reports a preview of the whole input, not the exact invalid byte position. Binary intentionally skips validation, so callers must choose the correct strategy for user-visible charset conversion.

## Test Signals
No local unit tests. Behavior is simple enough that coverage likely comes from charset conversion paths.
