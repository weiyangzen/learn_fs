<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level_test.go -->
# sources/storage-engines/pebble/internal/problemspans/by_level_test.go

Purpose: datadriven tests for `ByLevel` behavior over mocked monotonic time.

Important APIs/functions: `TestByLevel` initializes seven levels with `InitForTesting`, parses `now` arguments, and supports commands `add`, `excise`, `overlap`, and `is-empty`.

Control flow and state: test time can only move forward. `add` lines include level plus bounds and absolute expiration time; the test converts this to a duration from current time. `excise` applies bounds to all levels. `overlap` checks a specific level and prints result. Every command appends a formatted `ByLevel` dump for fixture verification.

Dependencies and integration: uses datadriven fixtures, `crstrings.LinesSeq`, `parseSetLine` from `set_test.go`, and `testify/require`. Risks not covered include concurrent access, invalid level indexes, and high cardinality/performance. It does strongly validate expiration semantics and per-level isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level_test.go -->
