<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan.go -->
# sources/storage-engines/pebble/sstable/colblk/keyspan.go

## Purpose
`keyspan.go` implements columnar blocks and iterators for fragmented range deletions and range keys. The format stores unique span boundary user keys separately from per-`keyspan.Key` trailer/suffix/value columns, reducing repeated boundary storage across fragmented spans.

## Important APIs, Types, And Functions
`KeyspanBlockWriter` exposes `Init`, `Reset`, `AddSpan`, `KeyCount`, `UnsafeBoundaryKeys`, `UnsafeLastSpan`, `Size`, `Finish`, and `String`. `KeyspanDecoder` exposes `Init`, `DebugString`, `Describe`, and boundary search. `NewKeyspanIter` creates pooled iterators from a block-cache handle. `KeyspanIter` wraps `keyspanIter` with handle ownership and pooling; `keyspanIter` implements `keyspan.FragmentIterator` methods `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `Close`, `SetContext`, `WrapChildren`, and `TreeStepsNode`.

## Control Flow
`AddSpan` writes start/end boundaries, avoiding duplicate storage when an abutting span starts at the previous end key, and appends each contained `keyspan.Key` to trailer/suffix/value columns. `Finish` writes a four-byte custom header containing boundary-key count, then encodes boundary columns with boundary-key row count and key columns with key count. Decoding must call `DecodeColumn` manually for boundary columns because their row count differs from the block header's key count. Iteration binary-searches boundaries for seeks, then gathers the next non-empty span forward or backward and materializes keys from index ranges between adjacent boundary entries.

## State And Persistence Behavior
Persistent state consists of boundary user keys, boundary key-indexes, trailers, suffixes, values, and a custom boundary-count header. Iterator state tracks the current boundary index, reusable `keyspan.Span`, inline two-key buffer, optional synthetic prefix buffers, transforms, and cache handle. `KeyspanIter.Close` releases the handle and usually returns the iterator to a pool, with invariant-mode finalizers checking missed releases.

## Dependencies And Integration Points
The file integrates with `internal/keyspan`, `internal/base`, `sstable/block`, `sstable/blockiter.FragmentTransforms`, `treesteps`, and block-cache metadata initialized through `InitKeyspanBlockMetadata`. It serves range-deletion and range-key block iteration in SSTable readers.

## Risks
Correctness depends on input spans already being fragmented and sorted. Empty spans are tolerated only singly between non-empty spans; consecutive or terminal empty spans panic as corruption. Synthetic suffix support is limited to range-key set/delete semantics. Unsafe metadata casting and pooled iterator lifetime require disciplined `Close` calls.

## Test Signals
`keyspan_test.go` provides datadriven encode/decode/iterator coverage, synthetic transform coverage, pooled cache-handle iterator tests under concurrency, and benchmarks for range-deletion seek and next operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan.go -->
