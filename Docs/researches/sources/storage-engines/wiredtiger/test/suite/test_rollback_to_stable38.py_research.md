# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable38.py

Purpose: intended to test history-store btree truncation and fast-delete behavior during recovery RTS over a very large table. The test is currently skipped unconditionally for TSan-related stderr/cache-stuck concerns.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`, snapshot isolation, 50MB cache, `SimpleDataSet`, local `check`, `simulate_crash_restart`, `stat.conn.cache_hs_btree_truncate`, and `stat.dsrc.rec_page_delete_fast`.

Control flow: if not skipped, it would create a one-million-row table, pin a transaction, write one value, write another value, checkpoint, rollback by crashing/restarting, then assert history-store btree truncate and fast-delete page stats are positive.

State and persistence behavior: targets large-scale history-store cleanup and fast-delete interaction during recovery. The pinned transaction is meant to retain history before crash.

Dependencies and integration points: integrates recovery RTS, history-store btree truncation stats, fast-delete stats, and very large dataset creation.

Risks: currently disabled by `self.skipTest("Not compatible with TSan")`, so it provides no active coverage unless the skip is changed. If enabled, it is expensive and sensitive to sanitizer/runtime performance.

Test signals: active signal is the skip. Intended signals are positive `cache_hs_btree_truncate` and `rec_page_delete_fast` stats after restart.
