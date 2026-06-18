# sources/storage-engines/pebble/compaction_test.go

Purpose: Main compaction behavior suite covering selection, execution, automatic flush/compaction, manual compaction, version edit validation, tombstone/read-triggered compactions, corruption recovery, error cleanup, stats, shared storage pacing, marked-for-compaction persistence, and value-separation related rewrites.

Important APIs/types/functions: `newVersion`, `newVersionWithLatest`, `compactionPickerForTesting`, `runCompactionTest`, and tests including `TestPickCompaction`, `TestAutomaticFlush`, `TestValidateVersionEdit`, `TestCompaction`, `TestCompactionOutputLevel`, `TestCompactionTombstones`, `TestCompactionReadTriggeredQueue`, `TestCompactionReadTriggered`, `TestCompactionAllowZeroSeqNum`, `TestCompactionErrorCleanup`, `TestCompactionCheckOrdering`, `TestMarkedForCompaction`, `TestCompaction_UpdateVersionFails`, `TestCompactionErrorStats`, `TestCompactionCorruption`, and tombstone-density move optimization tests.

Control flow: The file combines table-driven tests and datadriven harnesses. `runCompactionTest` opens an in-memory DB with deterministic event listeners and a no-periodic scheduler, then handles commands for defining DB state, batching, building SSTs, compaction, auto compaction, async/cancelled compaction, fake ongoing compactions, blob/virtual rewrites, span policies, logs, metrics, ingest, and excise.

State and persistence: Uses in-memory VFS, manifest `VersionEdit`s, table/blob metadata, snapshots, table stats, remote in-memory storage, object provider state, and direct `d.mu` mutations for controlled internal states.

Dependencies and integration: Exercises `manifest`, `compact`, `objstorage`, `remote`, `sstable`, blob fetching, error VFS, snapshots, event listeners, problem spans, and helpers in `data_test.go`.

Risks: Heavy use of async compaction/flush state, direct internal mutation, and exact event strings. Tests mitigate flakiness with explicit waits, deterministic formatting, no-periodic scheduler, fake time, and in-memory storage.

Test signals: Very broad regression coverage for compaction correctness, scheduling, cancellation, cleanup, failure accounting, manifest fatal paths, corruption/problem-span recovery, and tombstone-density move boundaries.
