# sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteWriter.cs

Purpose: `ByteWriter` writes raw bytes and encoded strings into byte arrays or streams.

Important APIs/types/functions: byte and byte-array writers, ANSI fixed-field writers using code page 28591, UTF-16 little-endian array writers, null-terminated ANSI/UTF-16 array writers, stream byte writers, ANSI stream writer with zero fill, UTF-8, UTF-16LE, and UTF-16BE stream string writers.

Control flow: buffer overloads write/copy at offsets and optionally advance `ref int offset`. Fixed string methods truncate to field length; stream ANSI pads with zero bytes when shorter than the field.

State and persistence behavior: stateless except target buffer/stream mutation and offset advancement.

Dependencies and integration points: pairs with `ByteReader` and protocol serializers.

Risks: buffer string writes do not zero-fill unused fixed fields, so stale bytes can remain. Truncation is silent. Length calculations use `value.Length`, which can differ from encoded byte length for non-Latin1 fallback cases. No explicit bounds validation.

Test signals: round-trip string tests, fixed-field truncation/padding tests, offset accounting, stale-byte behavior for short buffer writes, and UTF-16 terminator placement.
