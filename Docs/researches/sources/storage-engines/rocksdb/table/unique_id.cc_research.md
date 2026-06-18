# sources/storage-engines/rocksdb/table/unique_id.cc

Purpose: implements stable SST unique-id generation, session-id encoding, external/public ID encoding, and debugging string formats. These functions derive IDs from table properties (`db_id`, `db_session_id`, original file number) and are explicitly long-term stable because SST IDs can be stored in manifests, caches, backups, or diagnostics.

Important APIs/functions: `EncodeSessionId()` packs entropy into a 20-character base-36 string, preserving all 64 lower bits and part of the upper bits. `DecodeSessionId()` accepts 13-24 base-36 characters and returns `NotSupported` for missing, short, long, or malformed input. `GetSstInternalUniqueId()` builds a 128-bit or 192-bit internal ID: word 0 preserves session lower bits, word 1 hashes DB identity and xors file number, and optional word 2 stores a second DB hash. `InternalUniqueIdToExternal()` and `ExternalUniqueIdToInternal()` apply a bijective hash with offsets so all-zero internal IDs map to all-zero external IDs. `EncodeUniqueIdBytes()`/`DecodeUniqueIdBytes()` convert numerical words to 16- or 24-byte fixed64 strings. `GetUniqueIdFromTableProperties()` and `GetExtendedUniqueIdFromTableProperties()` are public helpers over `TableProperties`.

State and persistence: no local persistent state is mutated, but the byte encodings and hash transformations are durable compatibility contracts. `force=true` allows fallback hashing of malformed session IDs for temporary/test IDs.

Dependencies and integration: uses `util/coding_lean.h`, `util/hash.h`, `util/string_util.h`, `rocksdb/unique_id.h`, and table properties. Integrates with SST metadata, cache key identity, manifest validation, and human-readable diagnostics through `UniqueIdToHumanString()`.

Risks and test signals: compatibility regressions are the main risk. Tests should pin known session encodings, decode error statuses, 16/24-byte length checks, zero mapping, bijective round trips, malformed forced generation, and file-number uniqueness for a fixed DB/session.
