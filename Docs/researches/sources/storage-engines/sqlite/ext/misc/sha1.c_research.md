# sources/storage-engines/sqlite/ext/misc/sha1.c

Purpose: registers SHA-1 helpers `sha1(X)`, `sha1b(X)`, and direct-only `sha1_query(SQL)`.

Important APIs/types/functions: `SHA1Context`, `SHA1Transform()`, `hash_init()`, `hash_step()`, `hash_step_vformat()`, and `hash_finish()` implement hashing. `sha1Func()` hashes a value; `sha1QueryFunc()` hashes SQL text plus read-only result rows. `sqlite3_sha_init()` registers functions.

Control flow: scalar hashing treats blobs as bytes and other non-null values as UTF-8 text, returning hex or binary digest. Query hashing prepares each statement, rejects non-read-only SQL, hashes an `S<n>:` segment and type-tagged row/column encodings.

State and persistence: per-call hash state only; query function executes read-only statements and writes nothing.

Dependencies/integration: SQLite scalar, prepare/step, readonly, and direct-only APIs. SHA-1 is for deterministic testing, not modern security.

Risks/test signals: arbitrary read-only query execution, endian-sensitive type encodings, stable statement text hashing, and SHA-1 cryptographic weakness. Test known vectors, blob/text/null behavior, binary length, multi-statement hashing, non-query rejection, and type-stable results.
