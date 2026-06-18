# sources/storage-engines/wiredtiger/test/suite/test_hs03.py

## Purpose

Ensures checkpoints do not perform excessive history-store reads when only a small amount of new work needs reconciliation.

## Important APIs, Types, and Functions

Defines `test_hs03`, `get_stat`, and `large_updates`; uses connection stats `cache_write_hs` and `cache_hs_read` across column, integer row, and string row formats.

## Control Flow

The test loads a large table, checkpoints, pins stable low, performs 10k timestamped updates to create history-store pressure, checkpoints, then advances stable through small increments. For each increment it updates one record, checkpoints, and measures history-store reads during that checkpoint.

## State and Persistence Behavior

State is history-store volume plus checkpoint read accounting. The cache is intentionally small to make history overflow the cache.

## Dependencies and Integration Points

Depends on `SimpleDataSet`, fast statistics, scenario generation, and timestamp controls.

## Risks and Maintenance Signals

The allowed HS read bound is heuristic (`<=200`) because eviction and checkpoint concurrency can skew behavior. The first `assertGreaterEqual(hs_writes, 0)` is a weak sanity check.

## Test Signals

Signal is bounded `cache_hs_read` growth for small checkpoint increments after a large HS workload.
