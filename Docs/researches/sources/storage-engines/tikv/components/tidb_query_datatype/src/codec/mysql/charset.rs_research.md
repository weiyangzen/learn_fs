# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/charset.rs

## Purpose
Defines charset name constants and the set of multi-byte charsets recognized by the MySQL codec layer.

## Important APIs, Types, And Functions
- Charset constants: `CHARSET_BIN`, `CHARSET_UTF8`, `CHARSET_UTF8MB4`, `CHARSET_ASCII`, `CHARSET_LATIN1`, `CHARSET_GBK`, and `CHARSET_GB18030`.
- `MULTI_BYTES_CHARSETS`: lazy static `HashSet<&'static str>` containing `utf8`, `utf8mb4`, `gbk`, and `gb18030`.

## Control Flow
There is no dynamic control flow beyond lazy initialization of the hash set. Callers can test whether a charset is multi-byte using membership in `MULTI_BYTES_CHARSETS`.

## State And Persistence Behavior
The only state is process-local lazy static initialization. There is no serialization or persistent storage.

## Dependencies And Integration Points
Depends on `lazy_static` and `std::collections::HashSet`. Charset constants are used by string conversion, field metadata handling, and validation paths that need MySQL-compatible charset names or need to distinguish single-byte from multi-byte charsets.

## Risks And Edge Cases
- Adding a new multi-byte charset requires updating `MULTI_BYTES_CHARSETS`; the comment explicitly calls this out.
- Constants are stringly typed, so callers must normalize charset names before membership checks if inputs may vary in case or aliases.
- Rust treats `utf8mb4` equivalently to UTF-8 at the string level, but MySQL length and validation semantics may require additional checks elsewhere.

## Test Signals
No local tests. Coverage is indirect through conversion and charset validation tests. A small direct test could assert multi-byte membership and exclude binary/ascii/latin1.
