# sources/storage-engines/pebble/internal/keyspan/filter.go

## Purpose
Provides a `FragmentIterator` adapter that filters keys within spans and skips spans with no remaining keys.

## Important APIs, Types, And Functions
`FilterFunc` receives an input `*Span` and reusable `[]Key` buffer, returning the retained keys. `Filter(iter, filter, cmp)` constructs a `filteringIter` wrapped in assertions. `filteringIter` implements all fragment positioning methods plus `SetContext`, `Close`, `WrapChildren`, and `TreeStepsNode`.

## Control Flow
Each positioning method delegates to the child iterator and calls `filter(span, dir)`. `filter` applies the callback, returns a reusable mutable span when keys remain, or advances `Next`/`Prev` in the current direction until a non-empty filtered span or exhaustion/error.

## State And Persistence Behavior
The wrapper reuses `i.span.Keys` across calls; returned spans are valid only until the next positioning method. It does not persist data and forwards context/close to the child.

## Dependencies And Integration Points
Uses `base.Compare` for assertions and `treesteps` for debug tree reporting. It integrates with range-key filtering paths that need to remove individual `Key` entries while preserving span bounds.

## Risks And Edge Cases
Callbacks may mutate the input span and must respect key ordering expectations. A filter that returns a slice backed by unstable memory can violate iterator lifetime assumptions. Skipping empty spans changes relative-position behavior if callers expected to observe gaps.

## Test Signals
`filter_test.go` checks no-op filtering and filtering by range-key kind through datadriven iterator commands.
