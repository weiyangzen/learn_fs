# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable13.py

Purpose: validates stable tombstone restoration across multiple variants: simple update/remove/update chains, aborted updates before stable remove, history tombstones, and stable remove combined with dry-run RTS. It covers row/column formats, prepared updates, dry-run mode, and worker counts.

Important APIs/types/functions: extends the RTS base; uses `large_updates`, `large_removes`, explicit cursor writes followed by rollback, `session.checkpoint`, `simulate_crash_restart`, runtime `conn.rollback_to_stable("dryrun=...")`, and `stat.conn.txn_rts_hs_restore_tombstones`.

Control flow: each test pins timestamps at 10, creates a stable value at 20, creates removals or mixed update/remove transactions around 30/40, adds newer unstable updates around 60, checkpoints, and restarts. The stable-remove variant performs a runtime RTS dry-run or real RTS before another checkpoint and restart.

State and persistence behavior: focuses on tombstones restored from the history store. The expected stable state after restart is no rows at stable/newer read timestamps while older reads see the original value.

Dependencies and integration points: depends on history-store tombstone support, recovery RTS, dry-run accounting, prepared timestamp behavior, and RTS log verification via the base class.

Risks: tombstone history is nuanced; aborted updates should not interfere with the stable remove, and dry-run must not mutate state. Counter expectations are exact (`restored_tombstones == nrows`) and may expose implementation accounting changes.

Test signals: visibility checks before and after restart plus exact `txn_rts_hs_restore_tombstones` counts. The dry-run branch verifies that a dry-run does not change final recovery behavior.
