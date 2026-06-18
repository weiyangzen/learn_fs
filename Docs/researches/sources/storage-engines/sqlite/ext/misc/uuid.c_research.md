# sources/storage-engines/sqlite/ext/misc/uuid.c

## Purpose
Implements UUID helper functions: `uuid()` generates RFC-4122 version-4 text UUIDs, `uuid_str(X)` canonicalizes UUID input to text, and `uuid_blob(X)` converts UUID input to a 16-byte blob.

## Important APIs, Types, And Functions
Helpers include `sqlite3UuidHexToInt`, `sqlite3UuidBlobToStr`, `sqlite3UuidStrToBlob`, and `sqlite3UuidInputToBlob`. SQL functions are `sqlite3UuidFunc`, `sqlite3UuidStrFunc`, and `sqlite3UuidBlobFunc`; `sqlite3_uuid_init()` registers them.

## Control Flow
`uuid()` obtains 16 random bytes, sets version nibble 4 and RFC variant bits, renders canonical lower-case text with hyphens. `uuid_str` and `uuid_blob` accept either 16-byte blobs or text with 32 hex digits, optional braces, and optional hyphens before byte pairs. Invalid input returns NULL. Blob rendering always uses network byte order.

## State And Persistence Behavior
There is no stored state. Generated UUID randomness comes from SQLite's randomness provider; persistence occurs only if callers store results.

## Dependencies And Integration Points
Depends on SQLite randomness and scalar function APIs plus C character classification. The conversion functions are deterministic and innocuous; `uuid()` is innocuous but not deterministic.

## Risks And Edge Cases
Input parsing validates hex shape but does not require version or variant bits for caller-supplied UUIDs. Optional hyphens are more permissive than only canonical placement. `isxdigit()` is called on input bytes from SQLite text; tests should stay mindful of locale/unsigned-char behavior.

## Test Signals
Tests should verify generated UUID shape/version/variant, canonicalization from upper/lower/braced/hyphen-flexible strings, blob-to-string and string-to-blob round trips, invalid length or stray characters returning NULL, and deterministic flags for conversion functions.
