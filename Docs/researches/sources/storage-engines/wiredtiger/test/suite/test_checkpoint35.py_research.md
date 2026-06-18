# sources/storage-engines/wiredtiger/test/suite/test_checkpoint35.py

Purpose: tests precise checkpoint with stable full-table data and later unstable updates. After crash restart, rollback-to-stable should not report aborted updates and stable data should remain intact.

Important APIs and types: `conn_config = "precise_checkpoint=true"`, `SimpleDataSet`, per-row timestamped writes, `simulate_crash_restart`, and `stat.conn.txn_rts_upd_aborted`.

Control flow: create one million rows at increasing timestamps while advancing stable, write unstable `value_b` updates to the first 99 keys at a future timestamp, checkpoint, crash/restart, assert RTS aborted count is zero, then scan all keys for the stable value.

State and persistence behavior: precise checkpoint is expected to avoid writing unstable updates that would need RTS cleanup. The checkpoint plus recovery should present only stable `value_a` data.

Dependencies and integration points: tests precise checkpoint, timestamp stability, crash recovery, and RTS statistics. It covers row and column store formats.

Risks: very large data volume may be expensive. It does not assert that unstable updates are absent before crash, only after recovery.

Test signals: `txn_rts_upd_aborted == 0` and every row reads `value_a`.
