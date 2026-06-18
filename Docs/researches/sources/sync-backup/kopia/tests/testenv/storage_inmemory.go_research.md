<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/storage_inmemory.go -->
# sources/sync-backup/kopia/tests/testenv/storage_inmemory.go

This file registers in-memory storage flags for in-process CLI tests. `storageInMemoryFlags` stores `repotesting.ReconnectableStorageOptions`, adds a required `--uuid` flag, and creates a reconnectable in-memory blob storage from those options.

Control flow is invoked through the custom storage provider installed by `NewInProcRunner`. On connect, it returns `blob.NewStorage` with `repotesting.ReconnectableStorageType` and the create/connect mode.

State is externalized in the reconnectable storage registry keyed by UUID. Dependencies are Kopia CLI storage provider APIs and blob testing support. Risks include UUID reuse causing unintended shared storage and in-memory-only behavior diverging from real backends. Test signal is in-process CLI repository creation/use.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/storage_inmemory.go -->
