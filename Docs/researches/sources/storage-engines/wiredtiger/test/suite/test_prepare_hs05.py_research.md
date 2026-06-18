# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs05.py

Purpose: verifies that aborting a prepared transaction restores the correct older history-store version when the latest committed state is a delete.

Important APIs and types: `WT_NOTFOUND`, `make_scenarios`, `cursor.remove`, debug `release_evict=true`, `ignore_prepare=true`, and timestamped reads.

Control flow: the test writes value1 at timestamp 2, then in one transaction writes value2 and removes the key at timestamp 3. It starts a prepared update to value3 at timestamp 4, forces eviction with `ignore_prepare=true` so the prepared update can become the on-disk version and older versions move to history store, rolls back the prepared transaction, checkpoints, and reads old and latest timestamps.

State and persistence behavior: after rollback, timestamp 2 should still read value1 from history store, while the latest state should remain deleted due to the timestamp-3 remove. The aborted prepared update must not resurrect value3.

Dependencies and integration points: history store restoration, prepared update rollback, tombstone handling, eviction, row and column formats.

Risks: the test intentionally evicts while a prepared update exists; incorrect eviction/reconciliation can lose the older value or clear the tombstone.

Test signals: timestamp 2 search returns value1, and an untimestamped/latest search returns `WT_NOTFOUND`.
