# sources/sync-backup/restic/internal/backend/file.go

Purpose: Defines backend file type identifiers and handles.

Important APIs and types: `FileType` enumerates `PackFile`, `KeyFile`, `LockFile`, `SnapshotFile`, `IndexFile`, and `ConfigFile`. `FileType.String` returns layout names, with pack files historically named `data`. `Handle` combines type, metadata flag, and name. `Handle.String` formats a shortened display form. `Handle.Valid` validates type and name requirements.

Control flow and state: There is no persistence. Validation permits nameless config handles but requires names for all other valid types.

Dependencies and integration: Concrete backends and layouts use `Handle` to derive storage paths. Cache logic uses `IsMetadata` for pack-file caching and Azure uses it for access-tier decisions.

Risks and test signals: Adding file types requires updating validation and string conversion. `file_test.go` covers display and validation basics.
