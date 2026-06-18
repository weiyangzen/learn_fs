<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp23.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp23.py

Purpose: Regression test for repeatedly deleting and restoring a key at successive timestamps, then attempting a conflicting remove from an older read transaction.

Important APIs/types/functions: `test_timestamp23` uses `SimpleDataSet`, timestamped begin/commit calls, cursor `remove`, `debug=(release_evict)` eviction, a second session, and checks for `WT_ROLLBACK`.

Control flow: The test pins oldest/stable at 1, writes key 5 and key 6 at commit 11, deletes key 5 at 21, restores it at 31, deletes it again at 41, and evicts the page through key 6. A second session reads key 5 at timestamp 12 and then tries to remove it. The remove must fail with rollback.

State and persistence behavior: The update chain includes values and tombstones newer than the oldest timestamp, then is reconciled through eviction. The older reader sees history but cannot write over a conflicting newer chain.

Dependencies and integration points: Exercises history-store conflict detection, reconciliation of deleted/restored keys, column-store and integer row-store behavior, and rollback error mapping.

Risks: The comments identify a previous column-store bug where the conflicting remove incorrectly succeeded and later reconciliation asserted. This remains a high-risk visibility/conflict area.

Test signals: The required `WT_ROLLBACK` on `cursor2.remove()` is the main signal; any success triggers explicit failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp23.py -->
