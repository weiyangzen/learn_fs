# sources/storage-engines/pebble/internal/rangekey/coalesce_test.go

## Purpose
This file provides datadriven tests for range-key coalescing, validating that range-key sets, unsets, and deletes resolve to the expected observable internal state.

## Important APIs, Types, and Functions
`TestCoalesce` runs `testdata/coalesce`. For each `coalesce` command, it parses a `keyspan.Span`, initializes an output span with the same bounds, calls `Coalesce(testkeys.Comparer.CompareRangeSuffixes, span.Keys, &coalesced.Keys)`, and returns the formatted span.

## Control Flow and State
Each datadriven command is independent. The test exercises parsing, coalescing, trailer sorting in the wrapper, and string formatting. It keeps no state between commands.

## Dependencies and Integration
The test depends on `datadriven`, `keyspan.ParseSpan`, and `testkeys.Comparer`. It ties coalescing semantics to Pebble's test range-suffix comparer.

## Risks and Gaps
The test only reaches the public `Coalesce` wrapper, so snapshot-filtered `CoalesceInto` behavior and `ForeignSSTTransformer` sequence rewriting need coverage elsewhere. The behavior under invariant panics for unsorted input is not directly asserted here.

## Test Signals
The datadriven fixture is the authoritative signal for expected shadowing behavior. Any coalescing change should update this fixture deliberately and consider user-iterator and compaction compatibility.
