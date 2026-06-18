# sources/storage-engines/wiredtiger/test/suite/test_rollback01.py

Purpose: ensures a cursor `next()` that gets forced into eviction under cache pressure can return `WT_ROLLBACK` without retrying indefinitely, and leaves the cursor unpositioned.

Important APIs and types: `wttest.skip_for_hook("disagg")`, `wiredtiger.wiredtiger_strerror`, `wiredtiger.WT_ROLLBACK`, debug `release_evict`, `conn.reconfigure(cache_max_wait_ms=...,cache_size=...)`, cursor `search_near`, `next`, and `get_key`.

Control flow: it creates a table, inserts 100 1KB values, evicts the page, positions a second read cursor near key 10, shrinks cache/max wait aggressively, starts a transaction that writes a 5MB value, waits for accounting, and loops calling `read_cursor.next()` until a rollback error is observed. It then asserts `get_key` fails because the cursor is unpositioned.

State and persistence behavior: the oversized uncommitted update creates cache pressure. The read cursor is expected to be pulled into eviction and rolled back rather than transparently retried.

Dependencies and integration points: cache accounting, eviction, rollback error propagation, cursor positioning state, and connection reconfiguration.

Risks: timing and cache pressure can be environment-sensitive; the loop and sleep are there to give accounting time to trigger.

Test signals: a rollback error occurs within 80 `next()` attempts, and subsequent `get_key` raises `/requires key be set/`.
