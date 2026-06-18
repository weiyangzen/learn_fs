# sources/storage-engines/wiredtiger/test/suite/test_verbose05.py

## Purpose

`test_verbose05.py` validates checkpoint-progress verbose logging volume. It ensures progress messages appear but are bounded for both small and large databases.

## Important APIs, Types, and Functions

The class uses `conn_config='statistics=(all),verbose=[checkpoint_progress:0]'`, size scenarios, helper `populate`, `WiredTigerCursor`, `statistic_uri`, and `stat.conn.checkpoint_pages_reconciled`.

## Control Flow

The test creates a small-page table, writes large string values, checkpoints, reads checkpoint pages reconciled as an upper-bound estimate, reads stdout, counts messages matching a checkpoint-progress regex, compares the count with logarithmic lower/upper bounds, cleans stdout, and disables verbose output.

## State and Persistence Behavior

Persistent state is the populated table and checkpoint output. The statistic cursor observes connection statistics after checkpoint.

## Dependencies and Integration Points

Depends on verbose checkpoint-progress logging, statistics cursors, checkpoint reconciliation, and Python helper cursors. It is skipped for disaggregated and tiered hooks because their checkpoint progress differs.

## Risks and Edge Cases

The log-count bounds depend on page counts and current progress throttling. Very small page counts can make logarithmic bounds tight.

## Test Signals

Signals are progress messages matching the expected text and a count between the computed lower and upper limits.
