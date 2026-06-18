# sources/storage-engines/pebble/internal/keyspan/get_test.go

## Purpose
Tests `Get` for span containment and error propagation.

## Important APIs, Types, And Functions
`TestGet` parses spans with `ParseSpan`, constructs `NewIter`, optionally wraps it with probe DSLs, and calls `Get(cmp, iter, key)` for each input key.

## Control Flow
Datadriven `define` resets the span set. `get` creates a fresh iterator, attaches probes when requested, iterates through input lines, and formats either the found span, nil, or an error.

## State And Persistence Behavior
The test uses only local buffers and span slices. No persistent state is changed.

## Dependencies And Integration Points
Depends on `datadriven`, `crstrings`, `testkeys.Comparer`, and probe helpers from `test_utils.go`.

## Risks And Edge Cases
Coverage depends on `testdata/get`; the test is narrow and intentionally does not validate malformed or overlapping input spans.

## Test Signals
Failures point to incorrect containment rejection after `SeekGE`, missed matches at span bounds, or swallowed child iterator errors.
