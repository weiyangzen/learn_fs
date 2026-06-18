# sources/storage-engines/pebble/metamorphic/history_test.go

## Purpose
`history_test.go` validates the history logger and reordering support used to compare metamorphic runs under concurrent execution.

## Important Tests
- `TestHistoryLogger` writes multi-line `Infof` and `Fatalf` messages, normalizes timestamps with a regexp, and checks exact `// HH:MM:SS.mmm TYPE: line` formatting.
- `TestHistoryFail` verifies `failRE` does not fail unmatched output, then stores an error when a recorded operation line matches.
- `TestReorderHistory` uses datadriven inputs in `testdata/reorder_history` to check operation-index reordering.

## Control Flow and State
The tests construct in-memory `bytes.Buffer` histories, call public methods, and inspect buffered strings or `h.Error()`. The reorder test delegates to `reorderHistory` after splitting input lines with `difflib.SplitLines`, mirroring production comparison.

## Dependencies and Integration Points
The file depends on `datadriven`, `difflib`, `testify/require`, and standard regex/string utilities. It is package-internal and directly tests unexported history helpers.

## Risks and Edge Cases
- Timestamp normalization keeps formatting deterministic while still checking that timestamps are present.
- The tests do not cover `Recordf after Close` panic behavior or `extractOp` malformed-line panics.
- The datadriven corpus is the main coverage for out-of-order concurrent history lines.

## Test Signals
Passing tests indicate comment log output remains ignorable, failure regexes are wired into `history.Error`, and concurrent execution histories can be normalized before comparison.
