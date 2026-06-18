# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/charset.rs

## Purpose
Implements charset adapters used by collators to validate and decode character units from byte strings.

## APIs, Flow, And State
`CharsetBinary` treats each byte as a character, always validates, and decodes one byte at a time. `CharsetUtf8mb4` validates with `str::from_utf8` and decodes a Unicode scalar using `core::str::next_code_point`, returning the character and byte length. `CharsetGbk` and `CharsetGb18030` are aliases of `CharsetUtf8mb4` because TiKV stores those character data as UTF-8 internally for this layer.

## Dependencies And Integration
Depends on the collation `Charset` trait and crate-level `Charset` enum. Collator implementations bind to these charset types to define valid input and character weight input types.

## Risks And Test Signals
The UTF-8 decoder uses unsafe `from_u32_unchecked` after `next_code_point`; correctness depends on the standard library iterator. GBK/GB18030 aliases are an integration assumption that storage uses UTF-8 bytes, not original encoded bytes. Collator tests indirectly cover decoding.
