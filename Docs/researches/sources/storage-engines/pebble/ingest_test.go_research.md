<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/ingest_test.go -->
# sources/storage-engines/pebble/ingest_test.go

## Purpose
This file is Pebble's broad ingest test suite. It exercises local SST ingestion, ingest-and-excise, shared and external tables, blob-backed value separation, flushable ingests, WAL recovery, file linking/copying, sequence-number rewriting, validation, cleanup, concurrent ingest/compaction races, and many-SSTable benchmarks.

## Important APIs, Types, And Functions
The tests call public APIs such as `DB.Ingest`, `DB.IngestWithStats`, `DB.IngestAndExcise`, `DB.IngestAndExciseWithBlobs`, `Download`, `Compact`, `Flush`, `ScanInternal`, and iterators. Test harness helpers include `testIngestSharedImpl`, `blockedCompaction`, `linkAndRemovePredicate`, `ingestCrashFS`, `noRemoveFS`, `fatalCapturingLogger`, and `testFileNumAllocator`.

## Control Flow
Datadriven tests build DBs and external files, ingest them, wait for flush or compaction state, and compare LSM/iterator/metric output. Regression tests construct precise races: pending commits before ingest target selection, flushable ingest WAL replay, concurrent compaction overlap, and crash-like file-number reuse after linking before manifest application.

## State And Persistence Behavior
The suite verifies manifest edits, file-number allocation, local link/copy behavior, remote/shared backing metadata, blob file mappings, L0 versus lower-level placement, ingest-as-flush persistence, WAL-disabled reopen semantics, and cleanup of linked table and blob objects on error.

## Dependencies And Integration Points
It integrates `vfs`, `errorfs`, `objstorageprovider`, `remote`, `sstable`, `valsep`, `manifest`, `keyspan`, `rangekey`, `record`, table filters, datadriven command helpers, and test comparers. The tests stress DB commit sequencing, memtable overlap detection, LSM overlap checking, validation jobs, event listeners, metrics, and object storage.

## Risks And Edge Cases
Coverage focuses on corrupt SST endpoints versus internal blocks, read-only errors, invalid excise spans, ingestion overlapping mutable/queued memtables and large batches, hidden link/remove errors, file reuse after crash, non-deterministic concurrent LSM placement, and stale blob mappings during WAL replay.

## Test Signals
This file is itself test coverage. It uses datadriven golden files plus direct assertions for returned stats, metrics, LSM descriptions, iterator output, value reads, manifest replay ordering, cleanup errors, and background/fatal error routing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/ingest_test.go -->
