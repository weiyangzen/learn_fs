<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager.go -->
# sources/storage-engines/pebble/wal/failover_manager.go

## Purpose
Implements the WAL manager for failover mode, where a logical WAL may be written across primary and secondary directories and the active directory can switch on write errors or unhealthy latency. It also manages secondary directory identity, probing for failback, WAL listing/obsolete accounting, recycling, stats, and goroutine lifecycle.

## Important APIs, Types, and Functions
`dirProber` probes primary health. `ValidateOrInitWALDir`, `readSecondaryIdentifier`, and `writeSecondaryIdentifier` manage stable secondary IDs. `failoverMonitor` watches a `switchableWriter` and switches directories. `failoverManager` implements `Manager` through `init`, `List`, `Obsolete`, `Create`, `ElevateWriteStallThresholdForFailover`, `Stats`, `Close`, and `Opts`. `logCreator` creates or reuses WAL segment files. `stopper`, `timeSource`, and ticker types coordinate background work and tests.

## Control Flow
Initialization ensures the secondary is writable by writing `failover_source`, opens both WAL directories, starts a stopper, creates a monitor/prober, initializes the recycler, and converts initial scanned logs into obsolete records while ratcheting minimum recyclable numbers. `failoverMonitor.monitorLoop` samples current writer latency/error; it switches immediately on errors, switches on latency above thresholds, enables primary probing when on secondary, and fails back when probe mean/max are healthy. `Create` constructs failover-writer options and asks the monitor to create a writer in the current directory. Closed writer/segment callbacks merge physical segments into sorted logical WAL records.

## State and Persistence Behavior
Persistent effects include secondary identity files, `failover_source`, WAL segment files, directory syncs, and recycled WAL renames. In memory, the manager tracks initial obsolete logs, closed logical WALs and their physical segments, current writer, recycler state, directory handles, failover stats, and monitor/prober state. `writeSecondaryIdentifier` syncs the file and containing directory to make the identifier durable. `Obsolete` either returns physical logs for deletion or adds eligible primary synchronously closed single-segment WALs to the recycler.

## Dependencies and Integration Points
Integrates with WAL `Options`, `Dir`, `Manager`, `Writer`, `Scan`, `LogicalLog`, `DeletableLog`, record log writers through `failover_writer.go`, `LogRecycler`, VFS APIs, event listeners, histograms, CockroachDB time/error helpers, and Pebble format/options code that stores secondary IDs.

## Risks and Edge Cases
`generateStableIdentifier` ignores the error return from `crypto/rand.Read`, so entropy failure would not be reported. Failover heuristics are intentionally arbitrary and may need tuning; high secondary error counts suppress switching from primary to a likely misconfigured secondary. `RecyclerForTesting` returns nil despite the manager having a recycler. If a recycled-file reuse fails after `Pop`, cleanup of old/new files is left to restart-era cleanup. Segment creation is asynchronous, so `writerClosed` may not know all segments; `segmentClosed` repairs that later.

## Test Signals
`failover_manager_test.go` covers prober sampling, monitor switching/failback, failover manager datadriven behavior, quiesce under latency injection, secondary writability validation, and randomized all-files-deletable accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager.go -->
