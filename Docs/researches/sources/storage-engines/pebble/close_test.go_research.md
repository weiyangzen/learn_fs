<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/close_test.go -->
# sources/storage-engines/pebble/close_test.go

## Purpose
Regression test ensuring `DB.Close` cancels background contexts and completes promptly even when background table-stats loading or compactions are blocked on remote object reads.

## Important APIs, Types, and Functions
`TestCloseWithBlockedRemoteIO` constructs a DB with remote storage, ingests an external remote file, enables blocking reads, then closes the DB with a timeout. `blockingRemoteStorage` wraps `remote.Storage`; `blockingObjectReader.ReadAt` blocks on `ctx.Done()` after blocking is enabled.

## Control Flow
The test writes an SSTable into the wrapped remote storage, calls `IngestExternalFiles`, then flips the storage into blocking mode. A goroutine calls `d.Close()`. If close cancels the database background context correctly, any blocked remote `ReadAt` returns `ctx.Err()` and close completes. If not, the test fails after 10 seconds.

## State and Persistence Behavior
The file uses in-memory local VFS and in-memory remote storage. The interesting state is cancellation state: `DB.Close` must transition background work from active to cancelled and wait for goroutines without hanging on remote I/O.

## Dependencies and Integration Points
Touches external-file ingestion, remote storage factories, SSTable writing, table stats loading, background compactions, context propagation through object readers, and DB close orchestration.

## Risks and Edge Cases
The timeout is necessarily coarse; it proves no hang in this scenario but not every remote I/O path. `blockingRemoteStorage.block` closes its channel once and is not designed for toggling. It assumes background activity attempts a read after ingestion or that close handles any in-progress read.

## Test Signals
The key signal is `d.Close()` returning nil before the 10-second timeout after remote reads are configured to block until context cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/close_test.go -->
