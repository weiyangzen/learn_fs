# sources/storage-engines/tikv/components/compact-log-backup/src/storage.rs

Purpose: models log-backup metadata in memory, streams metadata objects from external storage, applies migration-based filters, supports sharding by backupmeta path store ID, and persists/loads compaction migrations.

Important APIs and types: constants `METADATA_PREFIX`, `DEFAULT_COMPACTION_OUT_PREFIX`, `MIGRATION_PREFIX`, `LOCK_PREFIX`, `MIGRATION_APPEND_LOCK`; `MetaFile`, `PhysicalLogFile`, `LogFile`, `LogFileId`, `Epoch`, `LoadFromExt`, `CountObjectsExt`, `StreamMetaStorage`, `VersionedMigration`, `MigrationStorageWrapper`, `name_of_migration`, `id_of_migration`, `hash_migration`, and `hash_meta_edit`.

Control flow: `StreamMetaStorage::load_from_ext` creates an external-storage prefix stream and loads migrations into `MetaEditFilters`. Its `Stream` implementation maintains ordered prefetch: it fetches object names, filters fully compacted metadata, shard-filters by parsed store ID before reading, spawns metadata loading tasks, and yields loaded `MetaFile`s in input order. `count_objects` counts metadata and optionally computes `shift_ts` from backupmeta filename ranges. `MigrationStorageWrapper::write` serializes migration append with a remote write lock.

State and persistence: reads `v1/backupmeta`, writes and reads `v1/migrations`, and uses `v1/APPEND_LOCK` for migration append coordination. Metadata edits can delete full physical files, logical spans, or entire metadata files.

Dependencies and integration: central to `execute/mod.rs`, `SaveMeta`, sharding, checkpointing, and tests. Uses BR protobufs, external storage, retry helpers, protobuf parsing, CRC64 hashing, and TiKV tracing/statistics.

Risks: backupmeta filename parsing is required for shard mode and optional shift-ts calculation. `tokio::spawn(...).await.unwrap()` in callers assumes loader tasks do not panic. Migration filters are append-only and must remain deterministic because they influence future compaction input. Hashes are integrity identifiers, not cryptographic proofs.

Test signals: tests cover backupmeta parsing, concurrent metadata loading, custom prefixes, migration filter merging/application, shift-ts counting, parse failures, and shard-related execution paths.
