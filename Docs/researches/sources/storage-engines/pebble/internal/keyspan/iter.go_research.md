# sources/storage-engines/pebble/internal/keyspan/iter.go

## Purpose
Defines the core `FragmentIterator` interface and implements `Iter`, a simple in-memory iterator over already-fragmented, sorted spans.

## Important APIs, Types, And Functions
`FragmentIterator` specifies `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `Close`, `WrapChildren`, `SetContext`, and `treesteps.Node`. `SpanIterOptions` carries range-key block property filters. `Iter` stores comparer, span slice, and index; `NewIter`, `Init`, `Count`, and all positioning methods implement the interface.

## Control Flow
`SeekGE` binary-searches for the first span with `End > key`. `SeekLT` binary-searches for the last span with `Start < key`. `First`/`Last` set endpoints, and relative moves increment/decrement the index while allowing movement from exhausted-before or exhausted-after states according to the interface contract.

## State And Persistence Behavior
`Iter` borrows the provided span slice and returns pointers into it, so returned spans remain stable as long as the slice is stable. It has no persistence and `Close` is a no-op.

## Dependencies And Integration Points
Depends on `base.Compare`, `context`, and `treesteps`. It is the lightweight test/reference iterator used throughout keyspan tests and by simple span sources.

## Risks And Edge Cases
The iterator assumes input spans are fragmented and sorted consistently with the binary-search predicates. It does not enforce non-overlap or sort order itself unless wrapped by `Assert`.

## Test Signals
`iter_test.go` uses datadriven commands to verify seeking and relative movement over parsed span sets.
