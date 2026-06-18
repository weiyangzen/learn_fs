# sources/storage-engines/wiredtiger/test/suite/test_hs29.py

Purpose: reproduces a path where reconciliation can hold three history-store cursors simultaneously: normal reconciliation, delete/reinsert from position, and tombstone cleanup. The test is primarily a crash/assertion regression for cursor-management correctness.

Important APIs and functions: `test_hs29` uses `WiredTigerTestCase`, standard cursor operations, debug eviction cursor `debug=(release_evict=true)`, timestamp pinning, no-timestamp updates, checkpoint, and connection close.

Control flow: it creates a string-key table, writes two timestamped versions for keys `1` and `2`, evicts both keys to push history, opens an old reader at timestamp 2, removes key `1` without a timestamp, updates key `2` without a timestamp, advances stable to 20, checkpoints, and closes the connection to trigger final checkpoint/reconciliation.

State and persistence behavior: the old reader pins visibility while no-timestamp changes create globally visible update/tombstone cases that require history-store cleanup. Closing the connection forces the final reconciliation point where cursor nesting previously mattered.

Dependencies and integration points: integrates history-store reconciliation, no-timestamp update semantics, tombstone cleanup, debug eviction, and final connection shutdown checkpointing.

Risks and edge cases: the test has no explicit post-close data validation; it relies on the absence of errors, assertions, or deadlocks. It is tightly tied to internal cursor acquisition order.

Test signals: success is completing checkpoint and `self.conn.close()` without WiredTiger errors or process aborts.
