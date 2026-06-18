<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager_test.go -->
# sources/storage-engines/pebble/wal/failover_manager_test.go

## Purpose
Tests the WAL failover manager, primary prober, monitor switching logic, secondary writability validation, graceful quiescence, and eventual deletion accounting for all physical WAL files.

## Important APIs, Types, and Functions
`manualTime` and `manualTicker` provide deterministic time. `TestDirProber`, `TestManagerFailover`, `TestFailoverManager_Quiesce`, `TestFailoverManager_SecondaryIsWritable`, and `TestFailoverManager_AllFilesDeletable` are the primary tests. Helper methods print prober and monitor state for datadriven outputs.

## Control Flow
`TestDirProber` initializes a prober with optional `errorfs` injectors and a blocking FS, enables/disables probing, advances manual time, blocks/unblocks IO, and queries mean/max samples. `TestManagerFailover` initializes a failover manager with manual thresholds, creates/writes/closes writers, blocks operations, advances monitor/prober time, lists stats, checks elevation state, and exercises obsolete behavior. The quiesce test uses `synctest` with random latency. The all-files-deletable test repeatedly creates WALs under latency, advances min-unflushed, calls `Obsolete`, deletes returned files, and eventually asserts no old logs remain.

## State and Persistence Behavior
Tests use MemFS directories for primary/secondary WALs and wrap them with error/latency/blocking layers. They create real in-memory WAL segments, secondary metadata, probe files, recycler state, and failover stats. Manual time makes background monitor/prober state deterministic.

## Dependencies and Integration Points
Covers `failover_manager.go`, `failover_writer.go`, `errorfs`, `vfs.MemFS`, WAL scanning/file accumulation, prometheus histograms, and the blocking FS helper defined in `failover_writer_test.go`.

## Risks and Edge Cases
Datadriven tests expose implementation details through channels to wait for goroutine iterations. The randomized all-files-deletable test can depend on timing but uses `Eventually` to absorb asynchronous segment callbacks. TODOs note missing prober history wraparound tests.

## Test Signals
Passing confirms switching/failback heuristics, stats updates, secondary preflight errors, goroutine shutdown, and physical WAL cleanup accounting remain functional.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager_test.go -->
