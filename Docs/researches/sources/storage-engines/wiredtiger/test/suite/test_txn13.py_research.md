# sources/storage-engines/wiredtiger/test/suite/test_txn13.py

## Purpose
`test_txn13.py` stress-tests very large logged transaction records. It expects 1 GB and 2 GB aggregate transactions to commit and a 4 GB aggregate to fail.

## Important APIs, Types, and Functions
The class defines dynamic `conn_config`, `test_large_values`, scenarios for row/column keys and value sizes, and uses `wttest.longtest`, `wiredtiger.WiredTigerError`, and `assertRaisesWithMessage`.

## Control Flow
For each scenario, the test creates a logged table with a 20 GB cache, builds a huge string prefix, inserts eight records inside one transaction, and either commits or expects a maximum-size error.

## State and Persistence Behavior
Large update values are logged as part of one transaction. Successful cases persist giant values; the oversized case must fail commit without pretending the transaction committed.

## Dependencies and Integration Points
Depends on WiredTiger log record sizing, Python memory capacity, cache configuration, and longtest scheduling.

## Risks and Edge Cases
This test is extremely memory/disk intensive. It also ignores long eviction warning output that can appear while handling huge values.

## Test Signals
`gotException` must equal `expect_err`; oversized scenarios match `/exceeds the maximum/`.
