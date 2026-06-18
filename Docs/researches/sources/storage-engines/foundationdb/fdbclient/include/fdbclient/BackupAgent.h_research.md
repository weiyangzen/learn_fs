# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BackupAgent.h

Purpose: high-level backup and restore orchestration API, including file backup, database backup/DR, task-bucket integration, key-backed configuration, mutation log helpers, and restore decoding utilities.

Important APIs and types: declares many boolean params controlling backup/restore behavior. `BackupAgentBase` defines state enum, key constants, time parsing/formatting, and status conversions. `FileBackupAgent` exposes restore overloads, atomic restore, abort/wait/status, submit/discontinue/abort backup, worker disable checks, task counts, and last restorable tracking. `DatabaseBackupAgent` handles DR-style backup, switchover, unlock, submit/discontinue/abort, status, and state lookups. Supporting types include `RCGroup`, `KeyBackedTag`, `TagUidMap`, `KeyBackedTaskConfig`, `BackupConfig`, `StringRefReader`, and tuple codecs.

Control flow: public methods generally wrap `ReadYourWritesTransaction` operations, task-bucket scheduling, and key-backed metadata updates. `BackupConfig::initNewSnapshot` clears snapshot maps, reads current version/interval, and initializes begin/target versions and counters. `getLatestRestorableVersion` combines log progress, snapshot progress, incremental mode, partitioned-log mode, and new BulkDump/BOTH snapshot modes.

State and persistence: extensive persistent state is stored in system keyspaces through `KeyBackedProperty`, `KeyBackedMap`, `TaskBucket`, tag maps, config subspaces, and backup containers. Task validation keys tie active tasks to non-aborted UID/tag pairs.

Dependencies and integration: integrates `NativeAPI.actor.h`, `TaskBucket`, `Notified`, `KeyBackedTypes`, `BackupContainer`, bulk dump/load modes, commit streams, system backup ranges, and transaction log key encodings.

Risks: this header is compatibility-sensitive: tuple codecs, key constants, and config fields must remain stable. Backup worker enable/disable races are explicitly noted around `submitBackup`. Multiple snapshot modes add restorable-version edge cases.

Test signals: backup/restore simulation tests, DR tests, task-bucket tests, and CLI status/JSON tests. Helper assertions and trace logging expose malformed blocks and backup errors.
