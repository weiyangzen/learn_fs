# sources/storage-engines/pebble/wal/reader.go

## Purpose
Defines the logical WAL discovery and reading layer for Pebble. A `LogicalLog` is a virtual WAL number plus one or more ordered physical segment files, allowing WAL failover to present a single replay stream even when writes moved between directories or log-name indexes.

## Important APIs, Types, And Functions
Key types are `LogicalLog`, private `segment`, `Logs`, `FileAccumulator`, and `virtualWALReader`. Public entry points include `Scan`, `FileAccumulator.MaybeAccumulate`, `FileAccumulator.Finish`, `Logs.Get`, `LogicalLog.OpenForRead`, `LogicalLog.PhysicalSize`, `LogicalLog.SegmentLocation`, and `Copy`. `appendDeletableLogs` converts every physical segment into deletion candidates.

## Control Flow
`Scan` lists every supplied WAL directory and feeds filenames into `FileAccumulator`. Accumulation parses `.log` filenames, binary-searches the logical WAL slice by WAL number, and binary-searches each WAL's segments by `LogNameIndex`, rejecting duplicates. `virtualWALReader.NextRecord` lazily opens the first segment, reads record fragments through `record.Reader`, buffers full records, skips malformed tails on non-final segments, parses batch headers, skips LogData-only batches, and deduplicates repeated batches by monotonically increasing sequence number. `Copy` replays a logical WAL through the virtual reader and writes a single destination WAL until the visible sequence boundary.

## State And Persistence Behavior
The file persists no metadata itself, but it maps durable physical WAL files into logical replay state. `Offset` tracks physical file path, physical offset, and bytes read from prior segments. `lastSeqNum` is transient deduplication state; `recordBuf` owns the record returned to callers until the next read. `Copy` creates a new physical WAL and syncs the writer on close, but explicitly leaves destination directory sync to the caller.

## Dependencies And Integration Points
Depends on Pebble batch headers, `record.Reader`/`LogWriter`, `vfs`, filename helpers from `wal.go`, and CockroachDB errors/redaction. Recovery uses this reader to replay virtual WALs, and managers use `LogicalLog`/`Logs` as the common inventory representation across standalone and failover modes.

## Risks And Edge Cases
Deduplication assumes WAL records contain valid non-LogData batches with increasing sequence numbers. Invalid batch headers are treated as corruption even if the record envelope is valid. Non-final segment tail corruption is ignored to tolerate failover/recycling, but final-segment corruption is surfaced to recovery policy. `Copy` must not leak destination files on mid-copy errors and must reject batches whose assigned sequence range straddles `visibleSeqNum`.

## Test Signals
`reader_test.go` covers listing, duplicate log indexes, segment ordering, virtual read behavior, corrupt/unclean tails, forced missing segments, logical copy limits, and copy error cleanup.
