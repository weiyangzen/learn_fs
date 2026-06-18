# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable29.py

Purpose: validates recovery RTS behavior when a no-timestamp update is written after timestamped history and removals. The no-timestamp value should remain globally visible after crash/restart.

Important APIs/types/functions: extends the RTS base; connection config enables small cache, statistics log, logging, and RTS verbosity. Uses `large_updates`, `large_removes`, an old reader transaction, `session.checkpoint`, `simulate_crash_restart`, and `stat.conn.txn_rts_hs_removed`.

Control flow: writes value A at 10, pins oldest/stable to 10, opens an old reader at read timestamp 10, removes at 30, writes value B at 40, checkpoints, writes value C at 50, then writes value D with no timestamp. It verifies value D at multiple timestamps, checkpoints, restarts, and rechecks value D.

State and persistence behavior: no-timestamp update supersedes timestamped history for visibility and must not be discarded by recovery RTS. The old reader helps preserve history-store content before later operations.

Dependencies and integration points: integrates logging, statistics logging, old-reader history retention, recovery helper, and RTS history-store cleanup.

Risks: no-timestamp semantics can mask older timestamped history; this is intentional. History-store removal counts are non-exact and only asserted nonnegative.

Test signals: value D visible at timestamps 10/20/40/50 and after restart; `hs_removed >= 0`.
