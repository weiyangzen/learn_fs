# sources/sync-backup/casync/src/cachunkid.c

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.c -->
## sources/sync-backup/casync/src/cachunkid.c

Purpose: `cachunkid.c` implements parsing, formatting, hashing, and path formatting for fixed 32-byte casync chunk IDs.

Important APIs and functions: `ca_chunk_id_parse` decodes a 64-character lowercase hex string into `CaChunkID`. `ca_chunk_id_format` encodes a chunk ID as lowercase hex. `ca_chunk_id_make` hashes data through a caller-provided `CaDigest` and copies the digest into a chunk ID. `ca_chunk_id_format_path` creates sharded paths using the first four hex characters as a directory and the full hex ID as the filename, with optional prefix and suffix.

Control flow: parser decodes two nibbles per byte and rejects non-hex or trailing characters. Formatter writes two hex chars per byte and a NUL terminator. Maker validates digest, data pointer, size limits, and digest size, then resets/writes/reads the digest. Path formatting first writes the full ID after the directory separator area, copies the first four ID characters into the shard directory, inserts `/`, and appends suffix if present.

State and persistence: no persistent state by itself. Its path format determines on-disk layout for cache and chunk files.

Dependencies and integration points: depends on `cadigest`, `cachunk` for size limits, and logging/util headers. Used by `cacache.c`, `cachunk.c`, and any code that names chunks.

Risks: parser accepts only lowercase `a-f`, not uppercase. `ca_chunk_id_format_path` assumes caller-provided buffer matches `CA_CHUNK_ID_PATH_SIZE`. Incorrect prefix/suffix sizing can overflow if callers ignore the macro. `ca_chunk_id_make` reuses and mutates the digest context.

Test signals: tests should cover parse/format round-trips, invalid hex, uppercase rejection if intentional, path formatting with/without prefix/suffix, and digest size mismatch.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.c -->
