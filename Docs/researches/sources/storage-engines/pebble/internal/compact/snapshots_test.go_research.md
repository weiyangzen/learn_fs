# sources/storage-engines/pebble/internal/compact/snapshots_test.go

## Purpose
This file tests the `Snapshots.IndexAndSeqNum` boundary behavior used by compaction stripe selection.

## Important APIs, Types, And Functions
`TestSnapshotIndex` is a table-driven test over `Snapshots`, input sequence numbers, expected index, and expected returned snapshot sequence.

## Control Flow
Each case constructs `Snapshots`, calls `IndexAndSeqNum`, and checks both returned values with fatal assertions.

## State And Persistence Behavior
The test is pure and in-memory. It validates logic that later affects durable compaction output.

## Dependencies And Integration Points
It uses `base.SeqNum` and the `Snapshots` methods in `snapshots.go`.

## Risks And Edge Cases
The cases cover empty snapshots, equality with a snapshot boundary, values below/above boundaries, and duplicate snapshot values. It does not separately call `Index`, but `IndexAndSeqNum` uses it directly.

## Test Signals
Failures indicate incorrect snapshot stripe assignment, which would make `compact.Iter` collapse too much or preserve too much data.
