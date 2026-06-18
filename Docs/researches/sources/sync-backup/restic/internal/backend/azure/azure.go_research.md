# sources/sync-backup/restic/internal/backend/azure/azure.go

Purpose: Implements the restic `backend.Backend` interface for Azure Blob Storage.

Important APIs and types: `Backend` stores config, container client, connection count, default layout, and optional access tier. `NewFactory`, `Open`, `Create`, `Save`, `Load`, `Stat`, `Remove`, `List`, `Delete`, `Hasher`, `Properties`, `IsNotExist`, `IsPermanentError`, `Warmup`, and `WarmupWait` expose backend behavior. Internal helpers include `open`, `supportedAccessTiers`, `useAccessTier`, `saveSingleBlob`, `saveLarge`, and `openReader`.

Control flow and state: `open` builds a container URL using account name, endpoint suffix, and container, then chooses shared-key, SAS, Azure CLI, or default Azure credentials. `Create` probes or creates the container, with special tolerance for authorization failures from restricted tokens. `Save` chooses single `Upload` for files up to 256 MiB or block upload with 100 MiB blocks for larger files. `Load` delegates range validation to `util.DefaultLoad` and `openReader`; `List` pages blobs under the layout prefix.

Persistence and dependencies: Data persists as Azure blobs using the default restic layout. The backend uses MD5 for transactional validation and optional access tier selection. Dependencies include Azure SDK clients, `layout`, `location`, `util`, `backend`, `debug`, and restic errors.

Integration points: Registered by `NewFactory` and `backend/all`. It participates in repository creation/opening, retry wrappers, cache wrappers, and generic backend tests. `AccessTierArchive` is applied only to non-metadata pack files to keep metadata immediately readable.

Risks and test signals: Risks include credential-mode regressions, SAS token quirks, range-read short-file detection, memory usage for single uploads, block ID collisions if block content repeats, access-tier misapplication to metadata, and pagination/cancellation handling. `azure_test.go` runs the generic backend suite when environment variables are available, covers SAS token creation, and optionally tests large upload range reads.
