# sources/storage-engines/wiredtiger/test/suite/test_bug027.py

Purpose: regression for snapshots containing more than 256 transactions. It ensures many unresolved transaction IDs do not leak into checkpoint/recovery visibility.

Important APIs/types/functions: `SimpleDataSet`, `simulate_crash_restart`, `session_max=512`, multiple sessions/cursors, `session.checkpoint`, and helper `check`.

Control flow: create a nonlogged table, insert 1,000 baseline rows and checkpoint. Open 500 sessions, each begins a transaction and updates a different key to `value_b` without committing. Commit one independent update on the last row to `value_c`, checkpoint, verify a scan sees baseline values except the last row, simulate crash/restart, and verify the same view again.

State/persistence behavior: keeps 499 uncommitted updates live across checkpoint creation. The checkpoint and crash recovery must exclude uncommitted values while preserving the committed last-row value.

Dependencies/integration: transaction snapshot encoding, checkpoint, nonlogged table behavior, crash restart helper, and cursor iteration.

Risks/test signals: resource-heavy due to many sessions. Failures show as unexpected `value_b`, missing `value_c`, or recovery inconsistency.
