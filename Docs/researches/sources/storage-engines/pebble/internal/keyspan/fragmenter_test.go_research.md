# sources/storage-engines/pebble/internal/keyspan/fragmenter_test.go

## Purpose
Tests eager span fragmentation and provides shared span-building/formatting helpers used by other keyspan tests.

## Important APIs, Types, And Functions
`parseSpanSingleKey`, `buildSpans`, and `formatAlphabeticSpans` parse compact test diagrams and format fragments. `TestFragmenter` validates range-delete fragmentation and deletion decisions. `TestFragmenter_Values` covers range-key set values. `TestFragmenter_EmitOrder` checks emitted key trailer ordering.

## Control Flow
Datadriven `build` commands feed spans to `Fragmenter.Add` and `Finish`, recovering panics as output for invalid cases. `get` commands build a `NewIter` over fragments, use `Get`, and evaluate `CoversAt` at read sequence numbers.

## State And Persistence Behavior
All state is in-memory: fragment slices, iterator references, and buffers. No files are written except datadriven golden updates when externally requested by the test runner.

## Dependencies And Integration Points
Depends on `datadriven`, `crstrings`, `base`, `require`, and package helpers. Its builders are reused by seek and truncate tests.

## Risks And Edge Cases
The compact parser is tailored to alphabetic diagrams and single-key spans, so it is not a general `Span` parser. The tests nevertheless cover important production invariants around ordering and visibility.

## Test Signals
Failures identify incorrect split boundaries, key aggregation order, range tombstone coverage, value retention, or input-order invariant enforcement.
