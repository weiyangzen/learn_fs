<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.c -->
# sources/user-network-fs/samba/source4/samba/server_util.c

## Purpose

`server_util.c` provides shared server utility code for tevent tracing and periodic log-size enforcement.

## Important APIs, Types, and Functions

`struct samba_tevent_trace_state` records event count and last log-size check time. `create_samba_tevent_trace_state()` allocates zeroed state. `samba_tevent_trace_callback()` watches `TEVENT_TRACE_BEFORE_WAIT` points and periodically calls log-size checks under root privileges.

## Control Flow

The main server and prefork masters create trace state and register the callback with `tevent_set_trace_callback()`. On each before-wait trace point, the callback increments an event counter and triggers a check every 200 events or after roughly 29 seconds. It forces the log-size check path, verifies whether a check is needed, temporarily raises privileges, and calls `check_log_size()`.

## State and Persistence Behavior

Only in-memory counters are stored. The side effect is external log-file rotation or truncation through Samba logging backends.

## Dependencies and Integration Points

It depends on tevent trace points, Samba debug/log-size helpers, and `root_privileges()`. `server.c` and `process_prefork.c` use it.

## Risks and Edge Cases

The check frequency is heuristic. If trace callbacks stop firing, log-size checks are delayed. Privilege elevation must be correctly scoped around `check_log_size()`.

## Test Signals

Tests can simulate tevent activity and verify `check_log_size()` is invoked after event-count or time thresholds, and that no action is taken for trace points other than `TEVENT_TRACE_BEFORE_WAIT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.c -->
