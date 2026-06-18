# Research: sources/storage-engines/pebble/version_set.go

## Purpose
`version_set.go` manages Pebble's sequence of immutable LSM versions and durable MANIFEST updates. It applies version edits, rotates manifests, tracks live/zombie/obsolete table and blob objects, maintains level metrics and compaction picker state, and locates the current manifest through an atomic marker.

## Important APIs, Types, And Functions
`versionSet` stores sequence-number atomics, object provider, DB mutex, options, filesystem, comparer, `manifest.VersionList`, latest-version mutable state, compaction picker, metrics, obsolete queues, zombie table/blob sets, WAL/manifest file numbers, manifest writer/file, rotation helper, and write serialization state.

`latestVersionState` tracks the L0 organizer, current blob file set, and latest virtual table backings. Initialization paths are `init`, `initNewDB`, and `initRecoveredDB`. Manifest write serialization uses `logLock`, `logUnlock`, and `logUnlockAndInvalidatePickedCompactionCache`. `UpdateVersionLocked` is the core apply path. Supporting functions include `getZombieTablesAndUpdateVirtualBackings`, `getZombieBlobFiles`, `createManifest`, `append`, `addLiveFileNums`, `addObsoleteLocked`, `setBasicLevelMetrics`, and `findCurrentManifest`.

## Control Flow
New DB initialization creates an empty version, compaction picker, initial MANIFEST snapshot, flushes and syncs it, syncs the directory, then moves the manifest marker. Recovered DB initialization installs recovered version state without rewriting the manifest.

`UpdateVersionLocked` serializes writers, calls a user update function, fills version-edit sequence and file-number fields, decides whether to rotate the manifest, updates virtual backings and blob file edit fields, drops `DB.mu` during manifest I/O, optionally creates a new manifest snapshot, encodes and syncs the edit, moves the marker after rotation, then reacquires `DB.mu` to update L0 metadata, zombies, obsolete queues, current version, manifest file number, metrics, and compaction picker.

## State And Persistence
Persistent state is the MANIFEST record stream plus `atomicfs` marker files pointing at the active manifest. Table/blob object liveness is represented in versions, blob file sets, virtual backings, zombie sets, and obsolete deletion queues. Sequence-number atomics govern WAL assignment and recovery. Directory sync before marker movement is part of the crash-safety contract.

## Dependencies And Integration Points
The file integrates manifest edit encoding/apply, record writers, object storage placement, delete pacing, virtual SSTables, blob rewrite heuristics, L0 organization, compaction picking, format-version gates, `vfs`, and `atomicfs.Marker`. It is on the critical path for flush, compaction, ingestion, recovery, and cleanup.

## Risks And Edge Cases
Manifest I/O errors after writing begins are fatal because partial durability is hard to reason about. `LastSeqNum` must remain at least every assigned sequence, including ingests. Manifest rotation must snapshot the pre-edit version and then append the edit. Virtual backing refcounts and `RemovedBackingTables` must stay consistent or table deletion can be unsafe. Marker movement relies on strict sync ordering. Metrics are recomputed in invariant builds to catch drift.

## Test Signals
Tests should exercise fresh and recovered initialization, manifest rotation, checkpoint reopen, sequence-number recovery, virtual backing create/delete/protect/unprotect, blob file deletion, zombie-to-obsolete transitions with live version refs, L0 organizer updates, metric recomputation, malformed marker names, and crash during large manifest writes.
