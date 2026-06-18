# sources/sync-backup/casync/src/cachunk.h

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.h -->
## sources/sync-backup/casync/src/cachunk.h

Purpose: `cachunk.h` declares chunk payload limits, compression representation choices, fd/in-memory conversion helpers, and chunk-file store operations.

Important APIs and types: `CA_CHUNK_SIZE_LIMIT_MAX` is 128 MiB and `CA_CHUNK_SIZE_LIMIT_MIN` is 1 byte. `CaChunkCompression` distinguishes `CA_CHUNK_UNCOMPRESSED`, `CA_CHUNK_COMPRESSED`, and `CA_CHUNK_AS_IS`. The API covers loading, saving, compressing, decompressing, opening chunk files, testing existence, loading/saving chunk files with desired/effective compression, marking missing chunks, and removing chunks.

Control flow contract: callers choose desired storage representation and a compression algorithm where relevant. `CA_CHUNK_AS_IS` is allowed for load/save desired behavior but not as an effective on-disk representation. `ca_chunk_file_load` can report the effective representation.

State and persistence: declarations map to chunk-store files managed by `cachunk.c`. The header itself does not expose store layout beyond requiring a cache fd, optional prefix, chunk id, and suffix-aware helpers.

Dependencies and integration points: includes `cachunkid.h`, `cacompression.h`, and `realloc-buffer.h`. It is used by higher-level encoder, store, and network code that needs consistent chunk limits and compression semantics.

Risks: callers must enforce ownership and lifetime for `ReallocBuffer` and fds. Passing inconsistent effective/desired compression values is rejected by implementation. The max-size constant is a hard safety limit and must stay aligned with protocol expectations.

Test signals: compile tests should exercise enum values and prototypes; runtime behavior is covered through `cachunk.c` tests and integration tests that write/read chunk stores.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.h -->
