# sources/storage-engines/pebble/internal/compact/spans_test.go

## Purpose
This file tests range deletion span compaction, range key span compaction, and splitting/encoding spans into SSTables.

## Important APIs, Types, And Functions
`TestRangeDelSpanCompactor` and `TestRangeKeySpanCompactor` run datadriven compact commands. `maybeParseInUseKeyRanges` parses optional in-use ranges. `TestSplitAndEncodeSpan` stores a span, encodes up to a key into an in-memory SST, reads it back, and prints encoded plus remaining spans.

## Control Flow
Compactor tests parse snapshots and in-use ranges, parse a `keyspan.Span`, instantiate the relevant compactor, compact into a reusable output span, and print either the span or `"."`. Split tests create a `MemObj`, `RawWriter`, call `SplitAndEncodeSpan`, close the writer, read back range deletions/range keys, and print both sides of the split.

## State And Persistence Behavior
Most tests are in-memory, but `TestSplitAndEncodeSpan` writes to an in-memory SST object to validate actual encoding/decoding behavior.

## Dependencies And Integration Points
It uses `datadriven`, `keyspan`, `sstable`, `colblk`, `objstorage.MemObj`, `testkeys`, and `require`. It validates `spans.go` together with SSTable span encoding.

## Risks And Edge Cases
The tests cover non-overlap ordering, snapshot stripe compaction, in-use elision, empty outputs, and partial range splits. They do not run the full compaction iterator/runner path, but they verify shared helpers in isolation.

## Test Signals
Signals are exact datadriven output for compacted spans and successful SST round-trip with at most one encoded span plus correct remaining span mutation.
