# sources/storage-engines/wiredtiger/test/suite/test_checkpoint34.py

Purpose: tests precise checkpoint behavior with an unstable fast truncate followed by crash restart. The unstable truncate should not require rollback-to-stable update aborts and original data must remain after recovery.

Important APIs and types: `conn_config = "precise_checkpoint=true"`, `SimpleDataSet`, `session.truncate`, `stat.conn.rec_page_delete_fast`, `simulate_crash_restart`, and `stat.conn.txn_rts_upd_aborted`.

Control flow: write 200,000 timestamped rows while advancing stable, reopen, perform an unstable truncate from midpoint to end at a later timestamp without advancing stable, confirm fast-truncate statistic, checkpoint, crash/restart, inspect RTS stats, then read all rows.

State and persistence behavior: precise checkpoint should avoid persisting unstable fast-truncate changes in a way that recovery must abort. All original stable values should be available after restart.

Dependencies and integration points: precise checkpoint, fast truncate, rollback-to-stable recovery, and crash simulation. Tiered hook is skipped.

Risks: large row count makes this a heavy test. It assumes `txn_rts_upd_aborted` stays zero because precise checkpoint prevented unstable update persistence.

Test signals: fast truncate pages are observed, RTS aborted update count is zero, and every key returns `value_a` after crash restart.
