# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable39.py

Purpose: tests checkpoint races where removed stable content and later updates interact with recovery RTS. It covers row/column formats and prepared/non-prepared updates.

Important APIs/types/functions: extends RTS base; uses `checkpoint_thread`, `simulate_crash_restart`, `large_updates`, `large_removes`, retry handling for rollbacks, `stat.conn.checkpoint_state`, and RTS statistics. `conn_config` enables checkpoint slow or history-store checkpoint delay timing stress depending on mode.

Control flow: writes value A at 20, removes at 30, sets stable around 30/40, starts checkpoint thread, writes value C and value B while checkpointing with retry-on-rollback behavior, simulates crash/restart, and validates the stable deleted state plus older history.

State and persistence behavior: the stable point is around a remove, while concurrent checkpoint may persist later updates. Recovery RTS should not count ordinary runtime RTS work and should preserve the stable deleted state.

Dependencies and integration points: integrates checkpoint thread timing, prepared operations, recovery RTS, and history-store stats.

Risks: rollbacks can occur while checkpoint is running, so update logic must retry. Timing affects whether history-store entries are removed or swept, and prepared mode changes stable boundaries.

Test signals: post-restart visibility checks, zero keys removed/restored/update-aborted/history removals for the first stat block, and later checks/stats demonstrating valid history-store cleanup when additional work is present.
