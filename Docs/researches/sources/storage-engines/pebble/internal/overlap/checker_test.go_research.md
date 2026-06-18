<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker_test.go -->
# sources/storage-engines/pebble/internal/overlap/checker_test.go

Purpose: datadriven tests for overlap detection using in-memory fake tables and iterators.

Important APIs/types: `TestChecker`, `testTable`, `testTables`, `newTestTables`, iterator factory methods `Points`, `RangeDels`, `RangeKeys`, helper `splitLinesInSections`, and `boundsFromSpans`.

Control flow and state: `define` commands build table metadata from points, range deletions, range keys, and optional override bounds. `overlap` commands build a `LevelMetadata`, optionally set `SkipProbe`, call `LevelOverlap` for each requested bounds line, and print result plus which iterators were opened. Fake iterator factories sometimes return nil for empty iterators to exercise nil-as-empty behavior.

Dependencies and integration: uses datadriven fixtures, `base.NewFakeIter`, `keyspan.NewIter`, manifest metadata bound extension methods, and `testify/require`. Risks covered include loose external-ingestion bounds, point/range split behavior, skip-probe pessimism, and iterator selection. Remaining gaps include whole-version `LSMOverlap`, real table reader errors, context cancellation, and concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker_test.go -->
