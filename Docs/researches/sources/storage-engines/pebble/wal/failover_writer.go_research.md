<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer.go -->
# sources/storage-engines/pebble/wal/failover_writer.go

## Purpose
Implements the failover-mode WAL writer. It writes records to the current physical `record.LogWriter`, retains unsynced records in a replay queue, asynchronously creates replacement segment writers on directory switches, and closes only when all queued records are durably written or a latest-writer creation/close error is known.

## Important APIs, Types, and Functions
`recordQueue`, `recordQueueEntry`, `poppedEntry`, `failoverWriter`, `failoverWriterOpts`, `logWriterAndRecorder`, `newFailoverWriter`, `WriteRecord`, `switchToNewDir`, `doneSyncCallback`, `Close`, `getLog`, and `latencyAndErrorRecorder` are central. Constants include `initialBufferLen` and `maxPhysicalLogs`.

## Control Flow
`WriteRecord` refs the caller's buffer, pushes the record into `recordQueue`, and if a current `record.LogWriter` exists, calls `SyncRecordGeneralized` with a pending sync index. `recordQueue` tracks `[tail, head)` with an atomic packed head/tail, grows as needed, snapshots outstanding records on writer switch, and pops records when a sync callback confirms durability. `switchToNewDir` reserves a physical log index, asynchronously creates/syncs the file and directory, wraps it in `SyncingFile` and `latencyAndErrorRecorder`, creates a `record.LogWriter`, and snapshots queued records into it if it is still latest. `Close` loops over created and creating writers, closes latest writers with the last queued record index, handles switches racing with close, pops any remaining entries with close error, and invokes manager callbacks.

## State and Persistence Behavior
Persistent state is physical WAL segment files named by logical WAL number and segment index in primary or secondary dirs. Queue state holds unsynced byte slices until a sync callback pops them and unrefs. Logical offsets are best-effort during periods before a writer exists or across failover replay. `getLog` exposes known segments with approximate sizes and whether they closed synchronously, enabling recycling only for safe segments.

## Dependencies and Integration Points
Integrates with `record.LogWriter`, WAL manager callbacks, `vfs.NewSyncingFile`, directory handles, metrics histograms, queue semaphores used by sync concurrency, failover monitor through `switchableWriter`, and `latencyAndErrorRecorder` for health sampling.

## Risks and Edge Cases
The queue can grow to the unsynced memtable-sized workload if callers do not request syncs. Logical offsets are approximate in some failover/no-writer cases, as comments document. Switching is capped at ten physical logs. Asynchronous segment creation means late-created unused files must be reported via `segmentClosed`. Close has complex races with monitor-triggered switches and stuck writers; errors from latest writer close/creation are fatal to callers.

## Test Signals
`failover_writer_test.go` covers datadriven switching, blocked IO, close modes, segment metadata, queue semaphore behavior, many-record queue growth, concurrent writer switches, and record continuity across physical segments.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer.go -->
