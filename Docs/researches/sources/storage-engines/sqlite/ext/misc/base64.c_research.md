# sources/storage-engines/sqlite/ext/misc/base64.c

## Purpose
`base64.c` implements a loadable SQLite scalar function `base64(x)` that converts BLOB input to RFC 4648-style base64 text and text input back to BLOB bytes.

## Important APIs, types, and functions
- Encoding tables/macros classify ASCII base64 digits, whitespace, padding, and invalid characters.
- `toBase64()` encodes bytes into base64 with linefeeds every 72 visible characters and after non-empty final output.
- `skipNonB64()` and `fromBase64()` decode text while tolerating whitespace and treating padding/dark non-digits as termination.
- `base64()` is the SQLite UDF dispatcher for BLOB-to-TEXT and TEXT-to-BLOB conversion.
- `sqlite3_base64_init()` registers `base64` as deterministic, innocuous, direct-only, UTF-8.

## Control flow
The SQL function checks the input SQLite type. For BLOB input, it estimates encoded size including linefeeds and terminator, enforces `SQLITE_LIMIT_LENGTH`, allocates text, encodes, and returns text with `sqlite3_free` as destructor. For TEXT input, it estimates decoded size, allocates a blob buffer, decodes, and returns a BLOB. Non-text/blob inputs produce an error.

## State and persistence behavior
The function is stateless. It allocates only per-call output buffers and stores no database state. Encoded output includes linefeeds, so serialized text is stable but not a single unbroken line.

## Dependencies and integration points
It depends on `sqlite3ext.h`, SQLite scalar function APIs, `sqlite3_limit()`, `sqlite3_malloc64()`, and `assert.h`. Macros at the end allow shell built-in integration under `SQLITE_SHELL_EXTFUNCS`.

## Risks and edge cases
- The implementation assumes ASCII-compatible UTF-8 for the first 128 codes and is not EBCDIC-safe.
- Decode accepts and skips non-base64 leading content and terminates on padding/non-digit cases, so strict validation is not the goal.
- Large inputs are constrained by SQLite length limits; allocation failures return `base64 OOM`.

## Test signals
Round-trip tests for empty blobs, one/two/three-byte tails, long line wrapping, whitespace in encoded text, invalid input termination, and length-limit failures provide coverage.
