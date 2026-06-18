# sources/storage-engines/sqlite/ext/fts5/fts5_varint.c

## Purpose
`fts5_varint.c` implements FTS5 variable-length integer serialization and deserialization for compact index, doclist, position-list, and btree storage.

## Important APIs, Types, And Functions
The main APIs are `sqlite3Fts5GetVarint32()`, `sqlite3Fts5GetVarint()`, `sqlite3Fts5PutVarint()`, and `sqlite3Fts5GetVarintLen()`. `sqlite3Fts5GetVarint32()` is a fast 32-bit decoder with unrolled 1-3 byte cases. `sqlite3Fts5GetVarint()` decodes 1-9 byte 64-bit varints. `sqlite3Fts5PutVarint()` writes small values inline and delegates larger values to `fts5PutVarint64()`.

## Control Flow
Decoding follows continuation bits, using unrolled cases and masks (`SLOT_2_0`, `SLOT_4_2_0`) to assemble payload bits. The ninth byte stores eight payload bits and terminates the sequence. Encoding emits low 7-bit chunks into a temporary buffer, clears the final continuation bit, reverses into the destination, and uses a special 9-byte path for full-width values.

## State And Persistence
The module has no state. It reads and writes caller-provided buffers. The byte encoding is part of the persistent FTS5 binary format, so compatibility is mandatory.

## Dependencies And Integration Points
It includes `fts5Int.h` for integer types and SQLite macros. FTS5 index and vocabulary code rely on this codec and related poslist decoding.

## Risks
The decoders assume valid caller-supplied buffers; truncation handling belongs to higher layers. Encoding changes would break existing indexes. The 32-bit fallback masks to 31 bits, so callers must choose the correct API. The unrolled code is performance-sensitive.

## Test Signals
Round-trip boundary values at every byte-length threshold, high 64-bit values, FTS5 rebuild/optimize behavior, and corruption tests that exercise malformed index bytes.
