# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable19.py

Purpose: validates RTS behavior for no-history and with-history delete/update chains across clean shutdown and crash restart paths. Scenarios include in-memory/disk, row/column keys, and restart mode.

Important APIs/types/functions: extends `test_rollback_to_stable_base`; imports `WT_NOTFOUND`; uses explicit cursor loops, `large_updates`, `large_removes`, debug eviction cursors, `session.checkpoint`, `simulate_crash_restart`, normal reopen/close behavior, and `stat.conn` counters.

Control flow: `test_rollback_to_stable_no_history` creates timestamped updates/removes without a stable history version, evicts deleted pages, sets stable to 20, then restarts or crashes and verifies no data is visible. `test_rollback_to_stable_with_history` first writes stable value at 20, removes at 30, mixes later updates/removes, evicts, sets stable to 40, restarts/crashes, and checks the expected stable/deleted views.

State and persistence behavior: distinguishes cleanup done during orderly shutdown from recovery-time RTS after crash. In-memory and clean-restart paths can have zero startup counters because work already happened during shutdown.

Dependencies and integration points: integrates eviction, checkpoint, recovery simulation, `WT_NOTFOUND` cursor search, and detailed RTS statistics.

Risks: stats are branch-dependent; interpreting clean shutdown like crash would be incorrect. Eviction and checkpoint order determines whether history exists and how counters are charged.

Test signals: visibility checks plus branch-specific assertions for aborted updates, history-store removals, key removal, and zero/positive behavior depending on `in_memory` and `crash`.
