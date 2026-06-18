# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint10.py

Purpose: stress-tests follower cursors when a new leader checkpoint is applied while the cursor is actively scanning. It focuses on monotonic ordering, bounds preservation, tombstone handling, completeness, and the `layered_curs_reopen_stable` statistic.

Important APIs/types/functions: helper methods format keys/values, insert/remove on leader/follower, `checkpoint_and_advance`, read follower stats, and start read-timestamp transactions. Uses `wiredtiger.stat.conn.layered_curs_reopen_stable`, cursor `next`, `prev`, `bound`, `reset`, and read timestamps.

Control flow: setup creates leader and follower connections and matching layered tables. Tests build combinations of checkpointed leader data and local follower ingest data, begin read-timestamp transactions, position cursors, scan partway, then insert more leader data and advance the follower checkpoint mid-scan. Variants cover forward/backward scans, bounded scans, follower tombstones, multiple checkpoint advances, and a restart-like continued scan after a key is removed and a new read timestamp is used.

State and persistence behavior: data is split between stable checkpoint content and follower ingest/local updates. Read timestamps determine visibility, while checkpoint pickup may reopen the stable side under an active cursor. Tombstones must remain hidden and order must not change.

Dependencies/integration points: cursor layering logic, follower checkpoint pickup, stable cursor reopening, transaction timestamp visibility, bounds, and tombstone reconciliation.

Risks: mid-scan switching is sensitive to exact cursor state. Some tests assert at least one statistic increment, so stat semantics changes can break tests even if behavior remains correct.

Test signals: pass indicates active follower scans survive checkpoint advances without skipped, duplicated, deleted, or out-of-order keys.
