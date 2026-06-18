# sources/storage-engines/sqlite/src/test_hexio.c

## Purpose

`test_hexio.c` supplies Tcl commands for byte-level database-file inspection and mutation using hexadecimal text, plus helpers for UTF-8 and FTS3 varint/record tests.

## Important APIs, types, and functions

Reusable helpers are `sqlite3TestBinToHex()` and `sqlite3TestHexToBin()`. Tcl commands are `hexio_read`, `hexio_write`, `hexio_get_int`, `hexio_render_int16`, `hexio_render_int32`, `utf8_to_utf8`, `read_fts3varint`, and `make_fts3record`. `getFts3Varint()` and `putFts3Varint()` implement FTS3 varint encoding.

## Control flow

`hexio_read` seeks and reads file bytes, converting them to uppercase hex. `hexio_write` decodes hex text, seeks, writes bytes, and returns the count. Integer commands render/parse big-endian or optional little-endian values. `utf8_to_utf8` runs malformed UTF-8 through debug-only `sqlite3Utf8To8()`. FTS commands consume or build byte arrays.

## State and persistence behavior

Only `hexio_write` persists changes, directly mutating files outside SQLite journaling. Other operations use transient buffers. Hex helpers are reused by `test_malloc.c`.

## Dependencies and integration points

It depends on `sqliteInt.h`, `tclsqlite.h`, C stdio, and debug-only UTF-8 internals. It supports pager, btree, encoding, corruption, and FTS tests needing exact byte control.

## Risks and test signals

Direct file writes can corrupt databases by design. Hex decoding ignores non-hex bytes and drops incomplete nibbles. Signals are exact hex reads, byte-count writes, endian conversions, debug availability errors, varint sizes, and generated FTS byte arrays.
