# sources/storage-engines/pebble/internal/keyspan/iter_test.go

## Purpose
Tests the simple in-memory `Iter` implementation over parsed span sets.

## Important APIs, Types, And Functions
`TestIter` uses datadriven `define` and `iter` commands, `ParseSpan`, `NewIter`, and `RunFragmentIteratorCmd`.

## Control Flow
`define` loads a span slice from test input. `iter` creates a fresh iterator over that slice, defers close, and runs scripted seek/first/last/next/prev operations.

## State And Persistence Behavior
All state is local to the test. No persistence or global mutation occurs.

## Dependencies And Integration Points
Depends on `datadriven`, `crstrings`, `base.DefaultComparer`, and test helpers. It provides a baseline signal used by many other tests' assumptions.

## Risks And Edge Cases
The test assumes well-formed input spans. It does not verify assertion behavior for unsorted or overlapping spans.

## Test Signals
Failures indicate binary search or exhausted-state behavior changes in `Iter`.
