# sources/storage-engines/pebble/snapshot.go

## Purpose
This file implements Pebble point-in-time snapshots and eventually-file-only snapshots. Ordinary snapshots pin a sequence number and participate in snapshot-list compaction constraints. Eventually-file-only snapshots reduce write amplification by transitioning from a normal snapshot to a version-pinning file-only snapshot after relevant memtables are flushed.

## Important APIs, Types, and Functions
`Snapshot` stores the owning DB, sequence number, optional EFOS backpointer, and links in `snapshotList`. It implements `Reader` with `Get`, `NewIter`, `NewIterWithContext`, `ScanInternal`, and `Close`.

`snapshotList` is a doubly linked list with `init`, `empty`, `count`, `earliest`, `toSlice`, `pushBack`, and `remove`.

`EventuallyFileOnlySnapshot` stores either a wrapped `Snapshot` or refcounted `manifest.Version`, protected key ranges, DB pointer, sequence number, and closed channel.

`DB.makeEventuallyFileOnlySnapshot` chooses the snapshot sequence number while avoiding overlap with ongoing ingest-and-excise operations, then either immediately refs the current version or registers a normal snapshot until memtables flush.

`transitionToFileOnlySnapshot`, `hasTransitioned`, `waitForFlush`, `WaitForFileOnlySnapshot`, `Close`, `Get`, `NewIterWithContext`, and `ScanInternal` implement the EFOS lifecycle and reader behavior.

## Control Flow
Regular snapshot reads delegate to DB internals with the fixed snapshot sequence. Closing removes the snapshot from `db.mu.snapshots`, updates wide tombstone earliest-snapshot state if the earliest snapshot advances, and schedules compaction.

EFOS creation loops while overlapping ingest-and-excise operations with future sequence numbers exist, waiting on `ongoingExcisesRemovedCond`. It checks protected ranges against memtables to decide whether it can be file-only immediately. If not, it creates a normal `Snapshot` and later `waitForFlush` forces or schedules flushes until all relevant sequence numbers are flushed; compaction/flush code then transitions it to a version ref.

EFOS iterators and `ScanInternal` choose snapshot options from the version ref if transitioned, otherwise from the sequence number alone.

## State and Persistence Behavior
Snapshots pin sequence numbers and can keep obsolete keys or files live. EFOS eventually releases the normal snapshot and pins a manifest version instead, increasing space amplification through zombie SSTable retention while avoiding memtable pinning. Closing releases snapshot-list membership or version refs and closes a channel used to signal waiters.

## Dependencies and Integration Points
This code integrates with DB mutex state, visible sequence numbers, memtable queues, flush scheduling, compaction scheduling, wide tombstone tracking, manifest version refcounts, ingest-and-excise bookkeeping, iterator construction, and `scanInternalImpl`.

## Risks
Lock ordering is critical: DB mutex before EFOS mutex. EFOS creation can starve if overlapping ingest-and-excise operations keep appearing. `Close` is not idempotent for EFOS and closes a channel directly. Snapshot methods panic on use after close. Incorrect transition timing around excise could expose pre-excise keys, which the comments and tests explicitly guard against.

## Test Signals
`snapshot_test.go` covers snapshot iteration, snapshot closure panics, range-deletion stress, snapshot creation race, and EFOS/excise race. `scan_internal_test.go` also exercises `ScanInternal` through snapshots and EFOS.
