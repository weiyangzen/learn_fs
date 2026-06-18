# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable42.py

Purpose: tests reopening a database after an RTS-needed file is deleted externally. It verifies WiredTiger handles missing files during shutdown/startup RTS without crashing.

Important APIs/types/functions: imports `test_rollback_to_stable_base` from `test_rollback_to_stable01`, uses `SimpleDataSet`, `os.remove`, `simulate_crash_restart`, `conn.set_timestamp`, `large_updates`, and `session.checkpoint`.

Control flow: skips tiered storage and Windows because file deletion assumptions are unreliable there. Otherwise it creates `table:test_rollback_to_stable42`, sets stable to 40, writes unstable updates, checkpoints them, removes the table file `test_rollback_to_stable42.wt`, and simulates crash/restart.

State and persistence behavior: deletion occurs after checkpoint so RTS would need the file during shutdown/startup. The intended state is an externally missing data file, not a logical table drop.

Dependencies and integration points: integrates filesystem behavior, recovery RTS, platform-specific skips, and tiered storage capability checks.

Risks: highly platform/storage-engine dependent; tiered storage can obscure file names, and Windows file locking prevents removal.

Test signals: successful restart without uncaught exception is the primary signal.
