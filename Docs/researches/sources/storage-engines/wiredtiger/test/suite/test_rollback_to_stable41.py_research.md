# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable41.py

Purpose: small focused test for `rollback_to_stable(dryrun=true)`: a dry-run must not remove unstable updates, while a subsequent real RTS must remove them.

Important APIs/types/functions: extends RTS base; uses `SimpleDataSet`, `large_updates`, `check`, `conn.set_timestamp`, and two calls to `conn.rollback_to_stable`, first with `dryrun=true` and then real with worker threads.

Control flow: writes value A at 10 and value B at 30, sets stable to 20, runs dry-run RTS and verifies value B is still visible, then runs real RTS and verifies reads at 30 return value A.

State and persistence behavior: no checkpoint or restart is involved; this isolates runtime dry-run behavior on in-memory state.

Dependencies and integration points: uses shared helper methods and worker-thread scenario coverage.

Risks: minimal; primarily catches accidental mutation in dry-run path.

Test signals: value B remains after dry-run; value A is restored after real RTS.
