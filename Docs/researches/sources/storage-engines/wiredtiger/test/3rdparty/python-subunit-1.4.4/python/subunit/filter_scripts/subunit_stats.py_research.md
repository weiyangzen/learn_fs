# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_stats.py

## Purpose

`subunit_stats.py` prints aggregate statistics for a subunit stream.

## Important APIs, Types, and Functions

`main()` calls `run_filter_script` with `StreamToExtendedDecorator(TestResultStats(stream))` and a `print_stats` post-run hook that calls `result.decorated.formatStats()`.

## Control Flow

The shared filter runner parses the stream, updates `TestResultStats`, invokes `print_stats`, unwraps to a result with `wasSuccessful` if needed, and exits 0 for no failures or 1 for failures.

## State and Persistence Behavior

`TestResultStats` keeps counters and a set of seen tags in memory. Output is a short text summary; no files are persisted unless redirected.

## Dependencies and Integration Points

It depends on `testtools.StreamToExtendedDecorator`, `subunit.TestResultStats`, and `run_filter_script`.

## Risks and Test Signals

The post-run hook assumes the result has a `.decorated` layer because of the stream adapter. `test_subunit_stats.py` validates empty streams, mixed pass/fail/error/skip/xfail streams, tag accounting, and exact formatted output.
