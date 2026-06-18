# sources/storage-engines/pebble/internal/compact/splitting_test.go

## Purpose
This file tests compaction output split decisions and the `Frontiers` callback heap.

## Important APIs, Types, And Functions
`TestOutputSplitter` parses grandparent table metadata and runs splitter decisions. `TestFrontiers` initializes frontiers from sorted key lists and advances over scan keys. `initTestFrontier` creates a frontier callback that steps through provided keys.

## Control Flow
For output splitting, the test builds a version with grandparents in L1, constructs an `OutputSplitter` with start key, optional limit, and target size, advances frontiers for input keys, and prints the chosen split. Frontier tests create multiple frontiers, call `Advance` for each scanned key, and print heap contents.

## State And Persistence Behavior
All state is in-memory. The tests model split decisions that would later shape durable table boundaries.

## Dependencies And Integration Points
It uses `datadriven`, `manifest.ParseTableMetadataDebug`, `manifest.NewVersionForTesting`, `base.DefaultComparer`, `testkeys`, and the `Frontiers`/`OutputSplitter` APIs.

## Risks And Edge Cases
The tests cover grandparent boundaries, limits, target-size thresholds, same-user-key avoidance, and frontiers whose callback returns multiple already-reached keys. They do not validate actual SST writer bounds; `run.go` handles that separately.

## Test Signals
Expected textual split keys and frontier states identify regressions in heap ordering, callback looping, and split heuristics.
