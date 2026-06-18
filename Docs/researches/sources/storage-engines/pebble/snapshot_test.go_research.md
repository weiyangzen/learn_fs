# sources/storage-engines/pebble/snapshot_test.go

## Purpose
This file tests ordinary snapshots and eventually-file-only snapshots for read consistency, closure semantics, range deletion correctness, snapshot creation atomicity, and EFOS interaction with ingest-and-excise.

## Important APIs, Types, and Functions
`TestSnapshotListToSlice` verifies linked-list insertion order.

`testSnapshotImpl` is a datadriven harness shared by `TestSnapshot` and `TestEventuallyFileOnlySnapshot`, using commands for DB definition, writes, deletes, merges, snapshots, compactions, DB state, and iterator movement.

`TestSnapshotClosed` verifies that using a closed snapshot panics with `ErrClosed`.

`TestSnapshotRangeDeletionStress` creates many snapshots around expanding range deletions and checks each snapshot's visible key count in parallel.

`TestNewSnapshotRace` exercises atomicity between sequence-number acquisition and snapshot list insertion under mutex contention and concurrent overwrite/flush.

`TestEFOSAndExciseRace` reproduces and validates a race fix around EFOS creation during a blocked ingest-and-excise.

## Control Flow
The shared datadriven harness rebuilds an in-memory DB per `define`, applies scripted operations, captures named readers, and drives iterators through commands. Stress and race tests use goroutines, channels, wait groups, and explicit mutex blocking hooks to force interleavings.

## State and Persistence Behavior
All state is in-memory. Snapshot maps are closed during cleanup. EFOS tests create protected ranges covering the snapshot test keyspace. The excise race test uses a private testing hook to block ingest apply while creating EFOS.

## Dependencies and Integration Points
Tests integrate with DB writes, flushes, compactions, `Reader` interface methods, VFS, private ingest hooks, range deletion visibility, and Go concurrency primitives.

## Risks
Race tests rely on timing and forced hooks. The range-deletion stress test is parallel and can surface data races or iterator bugs. The EFOS test depends on precise sequencing around ingest-and-excise visibility and file-only transition.

## Test Signals
Signals include stable datadriven iterator output, expected panics after close, exact key counts for historical snapshots under range deletions, no lost key during concurrent snapshot creation, and EFOS seeing only post-excise keys before and after file-only transition.
