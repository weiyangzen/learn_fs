<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate07.py

Purpose: Checks that truncating ranges containing prepared updates/removes fails correctly.

Important APIs/types/functions: `test_truncate07` uses `WT_ROLLBACK`, `WT_PREPARE_CONFLICT`, `prepare_transaction`, `session.truncate`, optional eviction/checkpoint scenarios, and a helper `truncate` that maps exceptions to WiredTiger return codes.

Control flow: The test writes baseline data at timestamp 10 and marks it stable. A second session modifies every other even key in the middle third and prepares at timestamp 20. The main session optionally evicts and checkpoints, then attempts to truncate a range covering prepared changes. The truncate must return `WT_ROLLBACK`, and the transaction is rolled back.

State and persistence behavior: Prepared updates remain unresolved while the truncate tries to delete across them. Optional eviction lets fast-delete metadata interact with prepared update visibility.

Dependencies and integration points: Integrates prepared transaction conflict detection, fast-delete, checkpointing, timestamp stable advancement, and row/column store behavior.

Risks: Prepared update interactions can return either rollback or prepare conflict depending on path; this test codifies the expected rollback behavior for range truncate.

Test signals: `err == WT_ROLLBACK` after truncate and no successful commit of the truncating transaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate07.py -->
