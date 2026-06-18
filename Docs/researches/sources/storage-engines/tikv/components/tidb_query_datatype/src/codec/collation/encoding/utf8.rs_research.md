# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/utf8.rs

## Purpose
Provides shared UTF-8-compatible decoding for `utf8mb4`, `utf8`, and `latin1` strategy types in this collation layer.

## Important APIs, Types, And Functions
`Utf8CompatibleEncoding` supplies a charset `NAME`. A blanket `Encoding` implementation validates with `str::from_utf8`. Concrete zero-sized types are `EncodingUtf8Mb4`, `EncodingUtf8`, and `EncodingLatin1`.

## Control Flow
`decode` tries to view the byte slice as UTF-8. On success it returns the same string bytes as owned `Bytes`; on failure it formats an invalid preview and returns `cannot_convert_string` with the concrete name.

## State And Persistence
Stateless strategy types only.

## Dependencies And Integration Points
Depends on shared `format_invalid_char`, `Error`, `Result`, and byte aliases from `encoding/mod.rs`. Selected by charset template macros in `collation/mod.rs`.

## Risks
`EncodingLatin1` being treated as UTF-8 compatible is a local compatibility choice; true Latin-1 byte decoding is not implemented here. Any caller expecting arbitrary `0x80..0xFF` Latin-1 bytes to decode will receive conversion errors.

## Test Signals
No local tests; validation is indirect through charset conversion behavior.
