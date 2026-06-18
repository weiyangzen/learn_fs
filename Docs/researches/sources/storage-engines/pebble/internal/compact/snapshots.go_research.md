# sources/storage-engines/pebble/internal/compact/snapshots.go

## Purpose
This file defines the snapshot sequence-number helper used to partition compaction processing into visibility stripes.

## Important APIs, Types, And Functions
`Snapshots` is `[]base.SeqNum`. `Index(seq)` returns the index of the first snapshot greater than `seq`, or `len(s)`. `IndexAndSeqNum(seq)` returns that index and snapshot sequence, or `SeqNumMax` if no greater snapshot exists.

## Control Flow
Both methods use binary search over an ascending snapshot slice. Compaction iterator code uses the returned index to decide whether versions are in the same snapshot stripe and whether a stripe is bottommost.

## State And Persistence Behavior
Snapshots are in-memory inputs from the DB's active snapshots. Their ordering affects durable compaction output because versions are collapsed only within stripes.

## Dependencies And Integration Points
The type depends on `base.SeqNum` and `sort.Search`. It is used by `Iter`, `RangeDelSpanCompactor`, and `RangeKeySpanCompactor`.

## Risks And Edge Cases
Callers must provide ascending snapshots. Duplicate snapshot numbers are tolerated by binary search but may create subtle stripe semantics; tests include duplicates. An empty slice maps every key to the bottom stripe with `SeqNumMax`.

## Test Signals
`snapshots_test.go` checks empty, single, multiple, boundary, and duplicate snapshot cases for both index and returned sequence.
