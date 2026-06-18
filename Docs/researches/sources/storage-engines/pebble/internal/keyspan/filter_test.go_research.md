# sources/storage-engines/pebble/internal/keyspan/filter_test.go

## Purpose
Tests the filtering iterator's ability to retain selected range-key kinds and skip spans with no retained keys.

## Important APIs, Types, And Functions
`TestFilteringIter` defines `makeFilter(kind)` callbacks and runs `Filter(NewIter(cmp, spans), filter, cmp)` through `RunFragmentIteratorCmd`. Supported datadriven filter modes are `no-op`, `key-kind-set`, `key-kind-unset`, and `key-kind-del`.

## Control Flow
The `define` command parses span text. The `iter` command selects a filter from command arguments, creates a new child iterator, wraps it, and executes scripted seek/first/last/next/prev operations.

## State And Persistence Behavior
Only local span slices and output strings are used. The iterator is closed after each run.

## Dependencies And Integration Points
Depends on `datadriven`, `base.InternalKeyKind`, `testkeys.Comparer`, and package-local parsing/execution helpers.

## Risks And Edge Cases
The test only filters by key kind; it does not exercise callbacks that rewrite suffix/value data or deliberately return slices with unusual backing storage.

## Test Signals
Failures indicate incorrect span skipping, direction-specific advancement after filtering out spans, or loss of bounds/key ordering in filtered output.
