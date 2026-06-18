# sources/storage-engines/wiredtiger/test/suite/test_log03.py

## Purpose
Tests `log.os_cache_dirty_pct` by measuring increased fsync activity as the dirty limit becomes more aggressive.

## APIs, Types, And Functions
Defines `test_log03` with custom `setUpConnectionOpen` and `setUpSessionOpen` returning `None` so each subtest opens its own home. Helpers populate 20,000 large string rows, read `stat.conn.fsync_io`, and open connections with variable `log=(file_max=...,os_cache_dirty_pct=...)`.

## Control Flow, State, And Persistence
`test_dirty_max` first establishes a baseline with 12MB log files and dirty pct 0. It recreates `HOME` for each run, writes enough data to produce log traffic, closes the connection, and compares fsync stats for dirty percentages 50, 33, 25, and 20. Lower percentages should trigger increasingly more fsyncs.

## Dependencies, Integration, Risks, And Test Signals
Depends on statistics fast mode, logging, OS-cache dirty threshold behavior, and large data writes. Risks include flaky fsync counts from environment variance, so expected increases are conservative. Signals are `assertGreater(result, baseline + increase)` for each threshold.
