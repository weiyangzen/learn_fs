# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable32.py

Purpose: tests runtime RTS in a case that triggers update-restore eviction and then validates subsequent writes/checkpoints remain correct. It covers row/column formats, prepared/non-prepared updates, and worker counts.

Important APIs/types/functions: extends RTS base; connection config uses 100MB cache, all statistics, and RTS verbosity. Uses `large_updates`, `large_removes`, `session.checkpoint`, `conn.rollback_to_stable`, explicit cursor no-timestamp or timestamped operations, and `check`.

Control flow: writes value A at 20, value B at 30, removes at 40, sets stable around 40/50 depending on prepare, writes value C at 60, checkpoints, verifies all states, runs RTS, then performs more writes/checkpoints and validates the stable value remains correct.

State and persistence behavior: RTS must handle a stable remove plus newer update and update-restore eviction side effects without corrupting later updates. Prepared scenarios use shifted stable timestamps.

Dependencies and integration points: relies on shared base helpers and WiredTiger reconciliation/update restore behavior.

Risks: exact behavior depends on whether pages are evicted and restored during checkpoint. Test comments indicate it is focused on update-restore eviction, so cache or eviction behavior changes can affect coverage.

Test signals: data checks before and after RTS, especially empty reads at stable remove timestamps and restored values after new updates.
