# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable37.py

Purpose: tests RTS dry-run versus real mode when a no-timestamp update exists after a long history chain. It ensures dry-run does not mutate state and real RTS retains the no-timestamp value.

Important APIs/types/functions: extends RTS base; connection config uses large cache, statistics log, logging disabled, and RTS verbosity. Uses repeated `large_updates`, an old reader at timestamp 10, checkpoints, `conn.rollback_to_stable('dryrun=...')`, and `stat.conn.txn_rts_keys_removed`.

Control flow: writes 300 timestamped versions of one key range, opens an old reader, writes value B at 2000, writes no-timestamp value C, writes value D at 3000, checkpoints, sets stable to 2000, checkpoints again, runs RTS in dry-run or real mode, then checks visibility around 1000/2000/3000.

State and persistence behavior: no-timestamp value C should be globally visible after real RTS, while dry-run should leave later value D visible at timestamp 3000. Old reader preserves historical content during setup.

Dependencies and integration points: integrates dry-run RTS mode, no-timestamp update semantics, history-store pressure, and stats.

Risks: dry-run and real branches intentionally expect different visibility at the newest timestamp. Misreading the scenario flag can look like corruption.

Test signals: branch-specific checks for value C versus value D and `keys_removed == 0`.
