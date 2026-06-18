# sources/storage-engines/wiredtiger/test/suite/test_reconcile02.py

Purpose: verifies reconciliation treats removal of already deleted keys from an old disk image as progress rather than reporting eviction blocked with no progress.

Important APIs and types: `SimpleDataSet`, debug cursor config `release_evict`, timestamped commits, `conn.set_timestamp`, and data-source statistic `cache_eviction_blocked_no_progress`.

Control flow: it inserts keys 1 and 2 at timestamp 10, deletes key 1 at timestamp 20, evicts the page, starts an uncommitted update to key 2 in another session, advances stable/oldest to 20 so the delete is globally visible, evicts again, then reads table statistics.

State and persistence behavior: the old disk image contains a deleted key that can be pruned during reconciliation. An uncommitted update remains in memory to make progress accounting relevant.

Dependencies and integration points: reconciliation, eviction, timestamp visibility, deleted-key pruning, and data-source statistics.

Risks: this test is sensitive to eviction actually running through the page; if debug eviction behavior changes, the stat may no longer measure the intended path.

Test signals: `cache_eviction_blocked_no_progress` for the table remains 0 after the second eviction.
