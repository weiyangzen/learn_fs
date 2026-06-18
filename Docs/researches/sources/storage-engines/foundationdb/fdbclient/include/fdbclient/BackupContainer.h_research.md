# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BackupContainer.h

Purpose: abstract interface and shared metadata for backup containers containing mutation logs, range files, snapshots, encryption metadata, and restore file sets.

Important APIs and types: `IBackupFile` is append-only with `append`, `finish`, and `size`. Metadata structs include `LogFile`, `RangeFile`, `KeyspaceSnapshotFile`, `SnapshotMetadata`, `BackupFileList`, `BackupDescription`, and `RestorableFileSet`. `IBackupContainer` defines create/exists, write log/range/tagged/range-partitioned files, write snapshot/partition files, read files, expire/delete, describe, list, restore-set lookup, container factory/listing, encryption setup, and URL/proxy accessors.

Control flow: concrete containers implement storage-specific operations while the interface standardizes how backup workers write data and how restore/management paths discover restorable data. `BackupDescription` can resolve versions to timekeeper timestamps. `RangeMapFilters` and `AccumulatedMutations` support mutation-log filtering and chunk reassembly.

State and persistence: backup state is durable in container files and optional metadata/properties. Version ranges, tag partitions, snapshot manifests, file sizes, encryption block size, and expired/unreliable boundaries encode restorability.

Dependencies and integration: includes Flow async file APIs, `NativeAPI.actor.h`, read-your-writes transactions, and FDB key/range types. Concrete implementations include filesystem/blob-backed containers.

Risks: filename formats and version constants are compatibility contracts. Expiration can make backups unusable if forced or if restorable checks are wrong. Range filters must match mutation semantics for point and range mutations.

Test signals: backup container list/describe/restore/expire tests; mutation-log decode and snapshot manifest tests; encryption setup tests.
