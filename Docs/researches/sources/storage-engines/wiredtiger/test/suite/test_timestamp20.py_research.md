<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp20.py

Purpose: Exercises correction of updates without timestamps in the history store, including full updates and modify chains.

Important APIs/types/functions: `test_timestamp20` uses `wiredtiger.Modify`, `debug=(release_evict)` cursors in `evict`, timestamped and no-timestamp transactions, checkpoints, and old-reader sessions.

Control flow: `test_timestamp20_standard` writes three timestamped versions for 9,999 keys, opens an old reader at timestamp 20, then writes two no-timestamp/current updates that should force history-store correction. After checkpoint and eviction, a read at timestamp 30 sees the no-timestamp value while the old reader sees the timestamp-30 value. `test_timestamp20_modify` repeats the pattern with modify records, keeping an old reader at timestamp 20 and verifying reconstructed modify history after later no-timestamp updates.

State and persistence behavior: The tests intentionally force pages to disk and into the history store, then evict them. They depend on transaction ID visibility and timestamp correction so old readers retain access to older versions while new timestamp reads do not bypass no-timestamp updates.

Dependencies and integration points: Integrates update-chain reconciliation, history-store writes, modify reconstruction, eviction debug hooks, and old-reader visibility.

Risks: Modify chains are sensitive to corruption because deltas can be applied to the wrong base value. No-timestamp updates can incorrectly shadow or expose history if correction logic is wrong.

Test signals: Value comparisons for all keys under current and old-reader transactions catch both visibility and reconstruction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp20.py -->
