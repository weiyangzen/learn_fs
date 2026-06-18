## sources/sync-backup/syncthing/lib/protocol/bep_fileinfo.go

Purpose: central file metadata model for BEP and the local database, including local invalid flags, conflict/equivalence logic, block metadata, block-size selection, hashes, and platform-specific ownership/xattr data.

Important types/functions: `FlagLocal` constants and `HumanString`; `BlockSizes` initialization; `FileInfo` with `ToWire`, `FileInfoFromWire`, `FileInfoFromDB`, `FileInfoFromDBTruncated`, string/log helpers, status methods, `BlockSize`, `FileSize`, accessors, `IsEquivalent`, `IsEquivalentOptional`, `InConflictWith`, and `WinsConflict`; utility functions `ModTimeEqual`, `PermsEqual`, `BlocksHash`, `VectorHash`; mutation helpers `SetMustRescan`, `SetIgnored`, `SetUnsupported`, `SetDeleted`; `BlockInfo`; `PlatformData`, `UnixData`, `WindowsData`, `XattrData`, and equality/conversion helpers.

Control flow and state: `init` builds valid block sizes from min to max and initializes the global protocol buffer pool after block sizes exist. `ToWire` serializes all public BEP fields and optionally DB-only internal fields; it panics if a truncated non-deleted/non-invalid/non-ignored file would be serialized. Incoming invalid wire state becomes `FlagLocalRemoteInvalid`. Equivalence first rejects must-rescan, masks ignored flags, compares identity/type/deletion/invalid state, ownership/xattrs/permissions according to options, then applies type-specific checks. Conflict detection uses version-vector dominance and previous/current block hashes. Setters for invalid/deleted states clear content.

Persistence behavior: local-only fields `LocalFlags` and `EncryptionTrailerSize` are serialized only when `withInternalFields` is true for DB storage. Truncated DB reads mark `truncated` to prevent accidental wire serialization without block data.

Dependencies and integration points: generated `bep` protobuf types, protocol vector/counter types, build platform flags, block constants, and global `BufferPool`. This file underpins scanning, syncing, database state, conflict resolution, encrypted metadata wrapping, and request block selection.

Risks: changes here have high blast radius. Equality semantics are subtle around invalid flags, permissions on Windows, ownership by ID/name, xattr ordering, and blocks-hash shortcuts. Platform data pointer comparisons are used as a fast inequality check before detailed comparison. Serialization panics guard against truncated misuse but can surface as runtime crashes if callers violate invariants.

Test signals: `bep_fileinfo_test.go`, `conflict_test.go`, encryption tests, and many model tests cover flags, equivalence, conflicts, consistency, and encrypted wrapping.
