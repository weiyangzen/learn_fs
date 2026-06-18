# sources/storage-engines/wiredtiger/bench/wtperf/idle_table_cycle.c

## Purpose
`idle_table_cycle.c` implements wtperf's optional helper thread that repeatedly creates, opens, closes, and drops idle tables while measuring whether those metadata operations exceed a configured threshold.

## Important APIs, Types, and Functions
Key functions are `check_timing`, `cycle_idle_tables`, `start_idle_table_cycle`, and `stop_idle_table_cycle`. It uses `WTPERF`, `CONFIG_OPTS`, `WT_SESSION`, `WT_CURSOR`, `wt_thread_t`, and `lprintf`.

## Control Flow
`start_idle_table_cycle` returns immediately when `max_idle_table_cycle` is zero. Otherwise it sets `idle_cycle_run`, creates a thread, and stores its ID. The worker opens a session, then while enabled sleeps one second, creates a new derived table URI, times create, opens/closes a cursor, times cursor open/close, drops with `force,checkpoint_wait=false` retrying `EBUSY`, and times drop. `stop_idle_table_cycle` clears the run flag and joins the thread.

## State and Persistence Behavior
The thread creates transient WiredTiger tables using `wtperf->uris[0]` as a prefix and drops them before the next cycle completes. Runtime state includes `wtperf->idle_cycle_run` and `wtperf->error`. Logs are emitted through wtperf logging.

## Dependencies and Integration Points
It depends on `wtperf.h`, WiredTiger sessions/cursors, `__wt_clock`, `WT_CLOCKDIFF_SEC`, `__wt_sleep`, thread helpers, and wtperf config fields. It mirrors similar behavior in workgen's idle table cycle.

## Risks and Edge Cases
The worker returns without closing the session on many error paths. It retries `EBUSY` on drop indefinitely until success or process shutdown. Performance thresholds can false-positive on slow or overloaded hosts. The URI buffer assumes generated names fit.

## Test Signals
Set `max_idle_table_cycle` in a wtperf config and verify no threshold warnings under normal load, errors when threshold is intentionally tiny/fatal, and clean thread shutdown.
