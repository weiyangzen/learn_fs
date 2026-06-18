# sources/test-tools/crashmonkey/code/results/TestSuiteResult.cpp

Purpose: implements aggregate counters and summary printing for reordering and timing/log-replay tests.

Important APIs/functions: `TallyResult()` increments pass/fixed/fsck-required/failed counters and failure subcategories. `TallyReorderingResult()` and `TallyTimingResult()` route to separate `ResultSet`s. `GetReorderingCompleted()`, `GetTimingCompleted()`, and `GetCompleted()` compute totals. `PrintResults()` emits human-readable summaries.

Control flow and state: `Tester` creates a suite at run start, tallies each `SingleTestInfo`, and prints summaries at the end.

Dependencies: consumes `SingleTestInfo`, `DataTestResult`, and `FileSystemTestResult`.

Risks: failed data-error tally uses a `switch` on exact `DataTestResult::GetError()`, so combined bitmask errors are not counted. There is no `default` in the inner switch. `total_tests` exists in `ResultSet` but is not updated. `auto_check_failed` is printed only for timing tests, not reordering tests.

Test signals: tally tests should cover every result category and data error, including combined errors and automated-check failures.
