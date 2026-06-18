# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable17.py

Purpose: tests repeated updates of the same key range where RTS should restore the stable value rather than delete keys. It runs row/column formats, in-memory/disk, and worker thread counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass using `verify_rts_logs`, local `insert_update_data`, local `check`, `conn.set_timestamp`, optional checkpoint, `conn.rollback_to_stable`, and stats including `txn_rts_upd_aborted` and `txn_rts_hs_removed`.

Control flow: creates a table, writes the same key range with values `aaaa`, `bbbb`, `cccc`, and `dddd` at increasing timestamps, sets stable to 5, checkpoints disk cases, runs RTS, then checks reads at timestamps 2 and 5 return the correct original/stable values while later timestamps return the stable value.

State and persistence behavior: stable keys must remain present and read as the timestamp-5 value after newer updates are discarded. If data is on disk, history-store cleanup may contribute to the stat total.

Dependencies and integration points: uses the WiredTiger test harness and `wiredtiger.stat`; does not use the shared base helper but mirrors its transaction patterns.

Risks: read timestamp selection must align with commits. In-memory and disk modes can produce different accounting, so the test combines update-aborted and history-store removed counts.

Test signals: value checks at 2/5/7/9 and `upd_aborted + hs_removed >= (nrows * 2) - 2`.
