# sources/storage-engines/wiredtiger/src/conn/conn_stat.c

## Purpose
This file initializes connection statistics and implements the optional statistics log server. It periodically writes connection and selected file statistics in text or JSON format and can also emit one final sample on close.

## Important APIs, Types, and Functions
Public entry points are `__wt_conn_stat_init`, `__wti_statlog_create`, and `__wti_statlog_destroy`. Important helpers include `__stat_config_discard`, `__statlog_config`, `__statlog_print_header`, `__statlog_print_table_name`, `__statlog_print_footer`, `__statlog_dump`, `__statlog_apply`, `__statlog_log_one`, `__statlog_on_close`, `__statlog_server`, and `__statlog_start`.

## Control Flow and Behavior
`__wt_conn_stat_init` refreshes cache, checkpoint timer, eviction, and transaction stats, then snapshots open-file, open-btree, open-cursor, dhandle, checkpoint dhandle, and reconciliation stash counters into connection stats.

Statlog create ignores read-only connections. It tears down any previous server or stale config, parses `statistics_log.wait`, `json`, `on_close`, path, source list, and timestamp format, and starts a dedicated internal session/thread if wait is nonzero. The server waits on a condition for the configured interval, then calls `__statlog_log_one` while enabled. Each sample opens or rotates the log file based on strftime path expansion, formats the timestamp, writes JSON headers if needed, dumps `statistics:` for the connection, and optionally walks open btree handles matching configured `file:` source prefixes after recovery completes.

Destroy clears the server flag, signals and joins the thread, destroys the condition, optionally logs on close, discards config and closes the log stream, and closes the statlog session.

## State and Persistence
Statistics counters live in memory; statlog output is persistent in configured files. State includes `conn->stat_log.path`, `format`, `fs`, `sources`, `stamp`, `usecs`, `session`, `cond`, `tid`, `tid_set`, and JSON table-state. Reconfiguration discards and rebuilds this state.

## Dependencies and Integration Points
The file uses statistics cursors, config parsing, file-system open/append/flush, local time/strftime, btree apply, recovery-complete flag, server flags, condition variables, internal sessions, and connection stat macros. It is started early in worker startup so other optional servers can observe statistics settings.

## Risks
Risks include malformed JSON grouping when statistic descriptions lack expected prefixes, statlog source races with intermittently removed objects, path/timestamp strftime failures, restarting statlog during reconfigure while users expect continuity, and on-close logging while a server is still running. The code handles busy/notfound stats cursors as nonfatal.

## Test Signals
Signals include text and JSON statlog files, source filtering for file objects, log rotation by path format, on-close output, read-only no-op behavior, reconfigure restart behavior, and valid JSON with both connection and table sections.
