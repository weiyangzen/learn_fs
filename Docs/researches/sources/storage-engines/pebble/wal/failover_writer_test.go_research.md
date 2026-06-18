<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer_test.go -->
# sources/storage-engines/pebble/wal/failover_writer_test.go

## Purpose
Tests failover writer behavior under switching, blocked IO, injected errors, close races, queue growth, and large record counts.

## Important APIs, Types, and Functions
`TestFailoverWriter` is a datadriven harness over crashable MemFS. `blockingFS` and `blockingFile` provide controllable blocking for create/write/sync/close/open-dir. `TestConcurrentWritersWithManyRecords` stresses queue resizing and multi-writer replay. `TestFailoverWriterManyRecords` writes four times the initial queue length. `randStr` and `seed` support randomized data generation.

## Control Flow
The datadriven harness initializes dirs, creates failover writers with optional injected errors or delayed writer creation, writes records with optional syncs, waits for queue length, switches dirs, closes synchronously or asynchronously, dumps logs after crash cloning, and inspects segment metadata. The concurrent test blocks all physical writers, writes thousands of unique records while periodically switching dirs, unblocks writes, closes, waits for syncs, and verifies each physical log contains a contiguous prefix interval and the final writer contains all records.

## State and Persistence Behavior
Tests use crashable MemFS and sync root/directories so printed log files reflect durable post-crash state. Queue semaphores model outstanding sync capacity. Blocking configuration is in-memory and released by closing channels. WAL segment files are read back through `record.Reader` to validate replay and sync behavior.

## Dependencies and Integration Points
Covers `failover_writer.go`, `record.LogWriter`, `vfs.NewCrashableMem`, `errorfs`, `LogNameIndex` naming, prometheus histograms, and the `stopper` lifecycle. `blockingFS` is also reused by manager tests.

## Risks and Edge Cases
The datadriven harness relies on sleeps and wait channels for async behavior. The concurrent test uses many records and may be relatively expensive, but it covers queue resize and pop races. TODO notes missing randomized error and delay injection tests.

## Test Signals
Passing indicates records are replayed correctly across switches, close propagates sync errors and metadata correctly, queue semaphores drain, and large queues do not lose or reorder synced records.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer_test.go -->
