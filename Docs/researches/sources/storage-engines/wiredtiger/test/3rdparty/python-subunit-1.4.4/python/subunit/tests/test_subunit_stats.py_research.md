# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_stats.py

## Purpose

`test_subunit_stats.py` tests `TestResultStats`, the result object used by stats and notification commands.

## Important APIs, Types, and Functions

`TestTestResultStats` sets up `StringIO` output, a `TestResultStats`, a `BytesIO` input stream, and `ProtocolTestCase`. It tests empty streams, mixed outcome streams, tag accumulation, and exact `formatStats()` output.

## Control Flow

`setUpUsedStream` writes a v1 subunit stream with global and local tags plus passed, failed, errored, skipped, and xfail tests, rewinds it, and runs through `ProtocolTestCase`.

## State and Persistence Behavior

All state is in memory: streams and result counters. No files are persisted.

## Dependencies and Integration Points

It depends on `unittest`, `BytesIO`, `StringIO`, `testtools.compat._b`, and public `subunit`. It validates `TestResultStats` for `subunit_stats.py` and `subunit_notify.py`.

## Risks and Test Signals

The tests confirm xfail counts as passed for stats purposes because only errors/failures increment failed and skips increment skipped. They also confirm seen tags are accumulated from tag events. Exact formatting checks protect command output stability.
