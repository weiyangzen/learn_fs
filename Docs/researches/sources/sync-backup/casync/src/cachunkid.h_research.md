# sources/sync-backup/casync/src/cachunkid.h

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.h -->
## sources/sync-backup/casync/src/cachunkid.h

Purpose: `cachunkid.h` defines the fixed-size `CaChunkID` type and helper API for chunk ID equality, null checks, digest creation, formatting, and path sizing.

Important APIs and types: `CA_CHUNK_ID_SIZE` is 32 bytes. `CA_CHUNK_ID_FORMAT_MAX` is 65 bytes including NUL. `CaChunkID` is a union of byte and u64 views. Functions parse, format, make IDs from digest/data, and format sharded paths. Inline helpers `ca_chunk_id_equal` and `ca_chunk_id_is_null` support comparisons. `CA_CHUNK_ID_PATH_SIZE(prefix, suffix)` computes buffer length.

Control flow contract: callers pass non-null buffers sized by the macros. Chunk IDs may represent SHA-256 or SHA-512/256 depending on digest context.

State and persistence: the type is embedded in cache and chunk-store records. The path macro defines the buffer contract used by store code.

Dependencies and integration points: includes `cadigest.h`, string/int headers, and relies on `strlen_null` for path sizing. Used throughout chunk, cache, index, and protocol code.

Risks: `ca_chunk_id_is_null` appears to loop over all u64 slots but checks `a->u64[0]` each iteration instead of `a->u64[i]`; a value with the first word zero and later words nonzero would be incorrectly reported null. This is a correctness bug if the helper is used for validation. The public union exposes representation and alignment assumptions.

Test signals: add a regression test where only a later `u64` lane is nonzero. Existing tests should also cover equality, null pointer behavior, and path size correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.h -->
