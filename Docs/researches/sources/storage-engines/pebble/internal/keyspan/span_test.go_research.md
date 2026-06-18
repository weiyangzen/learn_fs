# sources/storage-engines/pebble/internal/keyspan/span_test.go

## Purpose
Tests selected `Span` parsing and visibility/coverage helpers.

## Important APIs, Types, And Functions
`TestSpan_ParseRoundtrip` checks `ParseSpan(...).String()`. `TestSpan_Visible`, `TestSpan_VisibleAt`, and `TestSpan_CoversAt` use datadriven commands over `Span.Visible`, `VisibleAt`, and `CoversAt`.

## Control Flow
Each datadriven test defines one span and then evaluates sequence-number inputs, formatting the resulting span or boolean.

## State And Persistence Behavior
The tests use local span variables and buffers. No persistence occurs.

## Dependencies And Integration Points
Depends on `datadriven`, `crstrings`, and `base.ParseSeqNum`. It validates core semantics depended on by fragmenting, seeking, and merging tests.

## Risks And Edge Cases
A TODO notes that not all `Span` methods have direct unit tests. Sorting helpers, clone/copy behavior, smallest/largest key panics, and contains/bounds methods rely mostly on indirect coverage.

## Test Signals
Failures indicate parse/format drift, incorrect snapshot visibility, or coverage logic regressions around sequence numbers and batch visibility.
