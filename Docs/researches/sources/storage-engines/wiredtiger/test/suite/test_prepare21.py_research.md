# sources/storage-engines/wiredtiger/test/suite/test_prepare21.py

## Purpose

Regression test for prepared rollback interacting with rollback-to-stable, eviction, and a concurrent checkpoint.

## Important APIs, Control Flow, and State

The class inherits rollback-to-stable helpers, enables all statistics and `history_store_checkpoint_delay`, and uses `checkpoint_thread`. It writes value A at 20, B at 30, removes at 40, prepares value C at 50, verifies older reads, evicts pages with `ignore_prepare=true`, advances stable to 40, rolls back the prepared update, and writes value D at 60. A checkpoint thread starts; the test waits for checkpoint state via statistics, then evicts again while checkpoint is active. Final reads verify A, B, and D remain visible at their timestamps.

## Dependencies, Risks, and Test Signals

Dependencies include `test_rollback_to_stable_base`, `SimpleDataSet`, `checkpoint_thread`, and `stat.conn.checkpoint_state`. The risk is out-of-order timestamp/history fixup crashing during checkpoint. Signals are concurrent checkpoint synchronization, forced eviction, and post-operation timestamp reads.
