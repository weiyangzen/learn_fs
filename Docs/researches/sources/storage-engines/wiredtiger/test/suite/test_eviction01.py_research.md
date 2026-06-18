# sources/storage-engines/wiredtiger/test/suite/test_eviction01.py

## Purpose

Regression test for evicting update chains that contain only aborted updates, ensuring dirty eviction makes progress and does not block indefinitely.

## Important APIs, Types, and Functions

Defines `test_eviction01`, `get_stat`, and `test_eviction`; uses `SimpleDataSet`, `wiredtiger.stat.conn.cache_eviction_dirty`, and `cache_eviction_blocked_no_progress`.

## Control Flow

The test populates 100 rows, then repeatedly begins a transaction, updates nearly every row with a byte value, and rolls the transaction back. After 499 rollback-heavy iterations it checks eviction stats.

## State and Persistence Behavior

The workload creates long aborted update chains in cache without durable logical changes. Persistence is not the goal; eviction and cache state cleanup are.

## Dependencies and Integration Points

Depends on `wttest`, `SimpleDataSet`, and connection statistics.

## Risks and Maintenance Signals

Stat-based assertions can be sensitive to eviction scheduling, though the large iteration count is intended to force activity. It does not verify individual key values after rollback.

## Test Signals

Signals are dirty eviction count greater than zero and blocked-no-progress count equal to zero.
