# sources/storage-engines/wiredtiger/test/suite/test_cc02.py

Purpose: verifies checkpoint cleanup removes obsolete history-store content whether obsolete content remains in memory or has been evicted to disk.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, `stat.conn.checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_removed`, duration and handle stats, and debug eviction session `debug=(release_evict_page=true)`.

Control flow: populate 1,000 rows at timestamp 1, set oldest/stable to 1, update all rows at timestamp 10, set stable to 10, checkpoint so newer values are in the data store and older values in HS. In disk mode, read at timestamp 1 with release-evict to move HS pages to disk. Advance oldest to 10, force checkpoint cleanup, and assert visited/processed/duration stats plus either in-memory eviction or on-disk removal depending on scenario.

State/persistence behavior: intentionally makes timestamp-1 history obsolete by advancing oldest. Cleanup should mark in-memory obsolete pages dirty for eviction or remove on-disk obsolete pages.

Dependencies/integration: history store, checkpoint cleanup, eviction, Windows time granularity handling, and base helper timing loop.

Risks/test signals: different expectations for in-memory vs disk flow; timing stat check is skipped on Windows.
