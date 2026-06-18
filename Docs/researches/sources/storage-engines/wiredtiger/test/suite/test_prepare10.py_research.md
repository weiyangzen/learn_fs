# sources/storage-engines/wiredtiger/test/suite/test_prepare10.py

## Purpose

Checks that rollback of a prepared insert after committed deletes preserves correct time windows for concurrent readers and history-store retrieval.

## Important APIs, Control Flow, and State

The class uses `SimpleDataSet`, timestamped bulk `insert`/`remove` helpers, and read helpers using `ignore_prepare=true`. The test loads 1000 records with value A at timestamp 20 and value B at 30, checkpoints, opens long-lived reader transactions, removes all keys at 40, then prepares reinserts with value C at 50. It verifies snapshot readers at timestamps 20 and 35 see A/B while later reads see not found. After rolling back the prepared insert, the same visibility expectations remain, and the long-running sessions still observe their original snapshots.

## Dependencies, Risks, and Test Signals

Dependencies include WiredTiger constants, datasets, scenarios, checkpoints, and timestamp reads. The risk is that rollback of a prepared insert corrupts restored time windows or invalidates active snapshots. Test signals include two preserved reader sessions, `WT_NOTFOUND` at later timestamps, and repeated checks before and after prepare rollback.
