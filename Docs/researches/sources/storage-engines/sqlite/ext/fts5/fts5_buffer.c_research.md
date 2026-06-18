# sources/storage-engines/sqlite/ext/fts5/fts5_buffer.c

## Purpose
`fts5_buffer.c` implements small shared utilities used throughout FTS5: growable byte buffers, big-endian integer helpers, varint position-list readers/writers, allocation helpers, bareword classification, and a fixed-bucket term set used by integrity checking.

## Important APIs and functions
- `sqlite3Fts5BufferSize()` grows `Fts5Buffer` allocations exponentially from 64 bytes.
- `sqlite3Fts5BufferAppendVarint()`, `sqlite3Fts5BufferAppendBlob()`, `sqlite3Fts5BufferAppendString()`, `sqlite3Fts5BufferAppendPrintf()`, and `sqlite3Fts5BufferSet()` build byte/string buffers with shared `int *pRc` error propagation.
- `sqlite3Fts5Mprintf()` is a small `sqlite3_vmprintf()` wrapper that respects an existing error code.
- `sqlite3Fts5Put32()` and `sqlite3Fts5Get32()` encode/decode big-endian 32-bit integers for FTS5 record fields.
- `sqlite3Fts5PoslistNext64()`, `sqlite3Fts5PoslistReaderInit()`, and `sqlite3Fts5PoslistReaderNext()` decode FTS5 position-list streams into `(column << 32) + offset` values.
- `sqlite3Fts5PoslistSafeAppend()` and `sqlite3Fts5PoslistWriterAppend()` encode monotonically increasing positions, including column-change markers.
- `sqlite3Fts5MallocZero()` and `sqlite3Fts5Strndup()` centralize allocation and error-code handling.
- `sqlite3Fts5IsBareword()` classifies expression/config bareword characters.
- `sqlite3Fts5TermsetNew()`, `sqlite3Fts5TermsetAdd()`, and `sqlite3Fts5TermsetFree()` implement a duplicate-detection set keyed by index id plus term bytes.

## Control flow
Buffer append functions first ensure capacity, then append bytes and update `n`. String and printf appenders write a trailing NUL byte but keep it outside the logical length. Position-list decoding reads varint deltas. A value of 1 denotes a column change followed by column number and first offset; values greater than 1 are offset deltas plus 2. A value of 0 is treated as a terminator boundary. Encoding mirrors this by writing column markers when the high column bits change and offset deltas otherwise.

The term set uses the same checksum style as `fts5_hash.c` so collision-oriented tests can exercise both paths. On add, it checks an existing bucket for matching `iIdx`, term length, and bytes; if absent, it allocates one object containing the entry and term payload.

## State and persistence behavior
This file only manages transient memory. `Fts5Buffer` retains allocation capacity until freed or reused with `sqlite3Fts5BufferZero()`. Position-list helpers read/write serialized posting-list fragments that are later embedded in hash entries or index pages. `Fts5Termset` is in-memory only and is freed after integrity-check use.

## Dependencies and integration points
The implementation depends on `fts5Int.h`, SQLite allocation APIs, SQLite varint helpers declared in the header, and `assert_nc()` for corrupt-record-tolerant checks. It is used by config SQL assembly, expression phrase/NEAR evaluation, hash doclist construction, index page construction, auxiliary rendering, and integrity checks.

## Risks and edge cases
- Many functions are no-ops once `*pRc` is non-OK, so callers must initialize and inspect the shared error code correctly.
- `sqlite3Fts5BufferAppendString()` decrements `n` after appending `nStr+1`; it assumes the append happened or the buffer state remains valid under the error-code convention.
- `sqlite3Fts5PoslistSafeAppend()` silently ignores out-of-order positions. Callers must supply positions in nondecreasing order or matches disappear.
- `sqlite3Fts5PoslistNext64()` stops on corrupt records such as a column marker with an invalid first offset; callers must treat EOF plus `iPos=-1` as possible corruption depending on context.
- `sqlite3Fts5IsBareword()` indexes the ASCII table with `(int)t`; this relies on the high-bit early return for non-ASCII bytes.

## Test signals
Tests should exercise buffer growth, OOM propagation, NUL-terminated string append semantics, big-endian integer round trips, poslist encode/decode across columns and offsets, corrupt poslist boundaries, zero-length input, bareword parsing for ASCII and high-bit bytes, termset duplicate detection, and collision-heavy termset buckets.
