# sources/storage-engines/pebble/internal/compact/spans.go

## Purpose
This file compacts range deletion and range key spans and provides a helper to split and encode spans into output SSTables.

## Important APIs, Types, And Functions
`RangeDelSpanCompactor` and `MakeRangeDelSpanCompactor` coalesce RANGEDELs by snapshot stripe and elide bottom-stripe tombstones when allowed. `RangeKeySpanCompactor` and `MakeRangeKeySpanCompactor` coalesce range keys by suffix within stripes and elide bottom-stripe unset/delete keys. `SplitAndEncodeSpan` writes the prefix of a span before a table split key and keeps the suffix for the next table.

## Control Flow
Range deletion compaction scans trailer-descending keys, keeps the newest tombstone per snapshot stripe, stops after the bottom stripe, and may drop it if the range is not in use. Range key compaction partitions keys by snapshot visibility, calls `rangekey.Coalesce`, and filters unset/delete keys in the last stripe if elidable. `SplitAndEncodeSpan` encodes all, none, or a prefix depending on `upToKey`.

## State And Persistence Behavior
Compactors reuse output span slices and mutate span buffers. Their output is later persisted in SST range-del/range-key blocks. `SplitAndEncodeSpan` mutates the input span's `Start` to the remaining split point.

## Dependencies And Integration Points
It depends on `keyspan`, `rangekey`, `sstable.RawWriter`, snapshots, and tombstone elision. It is used by `Iter` and `Runner`.

## Risks And Edge Cases
Risks include preserving too many or too few range tombstones across snapshots, incorrect suffix coalescing, eliding range-key tombstones while lower range keys still exist, and split-key mutation bugs that duplicate or drop parts of a span.

## Test Signals
`spans_test.go` uses datadriven tests for range deletion compaction, range key compaction, in-use ranges, and split/encode behavior with actual SST reading.
