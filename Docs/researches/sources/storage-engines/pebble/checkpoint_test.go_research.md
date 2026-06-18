<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint_test.go -->
# sources/storage-engines/pebble/checkpoint_test.go

## Purpose
Tests checkpoint creation across local/shared storage, restricted spans, compactions, WAL durability, large manifests, and flushable ingest files.

## Important APIs, Types, and Functions
`testCheckpointImpl` is the datadriven harness over `testdata/checkpoint` and `testdata/checkpoint_shared`. It supports commands for opening DBs, applying batches, checkpointing, ingest/excise/build helpers, printing backing files, compacting, flushing, listing, scanning, and closing. `TestCopyCheckpointOptions`, `TestCheckpoint`, `TestCheckpointCompaction`, `TestCheckpointFlushWAL`, `TestCheckpointManyFiles`, and `TestCheckpointFlushableIngest` cover focused behaviors.

## Control Flow
The datadriven harness keeps named DB handles on a logging in-memory VFS plus optional in-memory remote storage. Checkpoint commands parse `restrict=start-end` spans and call `DB.Checkpoint`. The shared-storage variant configures `CreateOnSharedAll` and creator IDs. The compaction stress test concurrently writes keys, compacts, checkpoints 50 directories, and opens each checkpoint to verify all manifest-referenced non-virtual tables exist. The WAL flush test writes unsynced data, checkpoints with `WithFlushedWAL`, crash-clones unsynced data away, and verifies the checkpoint opens with the data. The flushable ingest test forces an overlapping ingest into the memtable queue, checkpoints, and verifies replay can open and read the ingested value.

## State and Persistence Behavior
Tests inspect filesystem operation logs, checkpoint directory listings, manifest-derived table references, WAL file size, virtual backing removal, and replay of flushable ingest records. All persistent state is modeled by in-memory or crashable VFS plus optional in-memory remote storage.

## Dependencies and Integration Points
The harness exercises DB open/close, batch commit, compaction, ingestion, excision, remote storage factory, SSTable writer, VFS logging, crashable memory, and table stats/cleanup waiting. It depends on datadriven files for expected operation traces.

## Risks and Edge Cases
The concurrency test is stress-style and may not deterministically hit every race. `TestCheckpointManyFiles` is skipped under `testing.Short`. Datadriven traces may be sensitive to iterator stack and file open behavior, which is why the harness pins `IteratorStackV1`. Shared-storage behavior is skipped on Windows.

## Test Signals
Signals include successful reopen of checkpoints, scans matching expected data, file operation traces, absence of missing SSTables during checkpoint/compaction races, durable WAL content after simulated crash, exact 10-key restricted checkpoint iteration in many-file tests, and successful WAL replay with pending ingested flushables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint_test.go -->
