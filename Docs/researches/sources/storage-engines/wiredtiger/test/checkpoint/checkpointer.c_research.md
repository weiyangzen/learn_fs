# Research: sources/storage-engines/wiredtiger/test/checkpoint/checkpointer.c

## sources/storage-engines/wiredtiger/test/checkpoint/checkpointer.c

Purpose: Service-thread and verification logic for the checkpoint stress test.

Important functions/APIs: `start_threads`, `end_threads`, `clock_thread`, `checkpointer`, `real_checkpointer`, `set_flush_tier_delay`, `prepare_discover`, `verify_consistency`, `compare_cursors`, `diagnose_key_error`, `do_cursor_next`, and `do_cursor_prev`.

Control flow: `start_threads` sets initial stable timestamp, starts the checkpoint thread, and optionally starts a clock thread. The clock thread advances stable/oldest timestamps, with special predictable-replay handling. `real_checkpointer` waits for tables, opens a session, repeatedly verifies online data, chooses a verification timestamp, checkpoints or flushes tier, verifies checkpoint and timestamp views, advances oldest timestamp, and sleeps for tiered/sweep timing. `prepare_discover` claims pending prepared transactions after recovery for precise checkpoint. `verify_consistency` opens cursors over all tables, optionally at a checkpoint or read timestamp, and compares key/value streams.

State and persistence: mutates global `g` timestamps, running flag, service thread handles, tiered flush delay, and checkpoint files. It validates persistent checkpoint content across tables.

Dependencies/integration: relies on `GLOBAL g`, worker-created tables/data, WT timestamps, tiered utility APIs, checkpoint cursors, prepare discover cursors, and disagg limitations. Risks include concurrency races, timestamp boundary choices, checkpoint cursor unavailability in disagg, and diagnostic cursor side effects. Test signals are printed checkpoint/verification milestones and fatal `log_print_err` updates to `g.status`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/checkpointer.c -->
