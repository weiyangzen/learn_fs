# sources/storage-engines/pebble/internal/compact/run.go

## Purpose
This file implements `Runner`, the data-writing half of compaction. It consumes `compact.Iter`, writes output SSTables and optional blob files, enforces output table splitting constraints, records pinned/missized statistics, and returns metadata required for version edits and cleanup.

## Important APIs, Types, And Functions
`Result`, `OutputTable`, `OutputBlob`, and `Stats` describe compaction output and errors. `RunnerConfig` supplies bounds, L0 split keys, grandparents, overlap limits, target file size, and a grant handle. `Runner` exposes `NewRunner`, `MoreDataToWrite`, `FirstKey`, `WriteTable`, `Finish`, and `TableSplitLimit`; helpers include `writeKeysToTable`, `validateWriterMeta`, and `spanStartOrNil`.

## Control Flow
`NewRunner` positions the iterator. Each `WriteTable` sets value-separation properties, appends an output table record, writes keys until an `OutputSplitter` asks to split or input is exhausted, finishes value separation, closes the writer, validates metadata, and records stats. Point keys go through `ValueSeparation.Add`; range spans are buffered and split/encoded around output table split keys.

## State And Persistence Behavior
The runner creates durable table/blob objects through supplied writers, but owns only metadata and accumulated stats. On failure, `Result` includes created objects for cleanup. Pending range spans may survive across table boundaries by keeping the unencoded suffix in `lastRangeDelSpan` or `lastRangeKeySpan`.

## Dependencies And Integration Points
It integrates `compact.Iter`, `OutputSplitter`, `sstable.RawWriter`, `objstorage`, manifest table/blob references, `valsep.ValueSeparation`, grant accounting, and compaction scheduler CPU/write-byte measurements.

## Risks And Edge Cases
Risks include output bounds exceeding compaction bounds or split keys, incorrect range-span splitting, writer close/metadata errors, value separation finish errors, pinned statistics undercounting range spans, and relying on approximate writer sizes for splitting.

## Test Signals
`run_test.go` validates `TableSplitLimit`. Span splitting is tested in `spans_test.go`, while full write paths are covered by broader Pebble compaction tests outside this subset.
