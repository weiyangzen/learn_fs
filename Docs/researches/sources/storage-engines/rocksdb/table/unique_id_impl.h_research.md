# sources/storage-engines/rocksdb/table/unique_id_impl.h

Purpose: declares internal unique-id representations and helper functions behind RocksDB's SST unique-id public API.

Important APIs/types: `UniqueId64x2` is the standard two-word ID; `UniqueId64x3` is the extended three-word variant. `kNullUniqueId64x2` and `kNullUniqueId64x3` reserve all-zero values as null sentinels. `UniqueIdPtr` is an implicit wrapper around either array type and exposes `ptr` plus `extended` so shared code can operate on both lengths.

Control flow and integration: callers compute an internal ID with `GetSstInternalUniqueId()`, optionally transform it with `InternalUniqueIdToExternal()`, then encode bytes for public surfaces. Reverse helpers exist mostly for tests. Session ID helpers bridge process/session randomness to compact filename-friendly IDs.

State and persistence: declarations emphasize long-term stability. Any change in binary layout, session encoding, or bijective transform can break stable SST identity, cache keys, and metadata verification.

Dependencies: includes `<array>` and `rocksdb/unique_id.h` for status/table-property-facing contracts.

Risks and test signals: `UniqueIdPtr` has no runtime size checks beyond the selected constructor, so callers must not pass insufficient storage. Tests should exercise both standard and extended forms, null sentinel invariants, external/internal round trips, and session ID entropy preservation.
