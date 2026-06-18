# sources/storage-engines/wiredtiger/test/suite/test_txn14.py

## Purpose
`test_txn14.py` verifies `session.log_flush` with `sync=off` and `sync=on`, confirming flushed logged updates survive simulated crash recovery.

## Important APIs, Types, and Functions
The class defines `mkvalue` and `test_log_flush`, scenarios for sync mode and key format, logging with small log files, and `simulate_crash_restart`.

## Control Flow
It creates a table, writes 10,000 rows, calls `log_flush` with the scenario sync value, writes five more rows, flushes again, simulates crash restart, scans the table, and verifies keys and values.

## State and Persistence Behavior
The transaction log is the persistence target. Both flush modes should ensure all writes before crash simulation are recoverable.

## Dependencies and Integration Points
Depends on WiredTiger log flush implementation, crash restart helper, and row/column key format behavior.

## Risks and Edge Cases
`sync=off` still requires records to be written enough for the simulated crash flow used by the test. Off-by-one scan assertions cover record count.

## Test Signals
After recovery, all `entries + extra_entries` rows are present with values `key + 1`.
