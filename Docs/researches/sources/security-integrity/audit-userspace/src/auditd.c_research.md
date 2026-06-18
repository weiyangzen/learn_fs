# sources/security-integrity/audit-userspace/src/auditd.c

## Purpose
`auditd.c` is the audit daemon main program. It parses CLI options, loads config, daemonizes, registers with the kernel audit subsystem, starts logging/dispatcher/listener subsystems, runs the libev event loop, handles signals, routes netlink events, and performs orderly shutdown.

## Important APIs, Types, And Functions
Important functions include signal handlers for TERM/HUP/USR1/USR2/CHLD/CONT, `update_report_timer`, `distribute_event`, `send_audit_event`, `become_daemon`, `alloc_pool_event`, `event_is_prealloc`, `netlink_handler`, `pipe_handler`, `reconfig_ready`, `main`, `clean_exit`, `get_reply`, and `getsubj`.

## Control Flow
`main` parses `-f/-l/-n/-s/-c`, sets foreground/background mode, ignores signals until libev owns them, loads config, checks capabilities, daemonizes if needed, opens netlink, creates runtime dir/pidfile, initializes events, libev, dispatcher, node name, reconfigure socketpair, start event, OOM adjustment, config manager, startup audit enablement, audit pid registration, signal/io/timer watchers, optional TCP listener, then enters `ev_loop`. Shutdown stops listener/watchers, emits end event, tears down dispatcher/events/config, and destroys libev.

## State And Persistence
Global state includes audit netlink fd, config, pid/state file paths, daemonization pipe, event pool, signal request atomics, subject buffer, audit session, report timer, and libev loop. It persists pid and state report files under `AUDIT_RUN_DIR`, emits audit daemon lifecycle records, and registers/unregisters the audit pid with the kernel.

## Dependencies And Integration
It integrates every major local subsystem: config, event, dispatch, listener, reconfig manager, libdisp, libaudit, libev, and common/private helpers. Kernel audit interaction uses `audit_open`, `audit_set_pid`, `audit_get_reply`, `audit_request_signal_info`, and related libaudit APIs.

## Risks
Risks include startup ordering failures leaving partial state, preallocated event pool exhaustion causing daemon abort, signal-info request races, using a socketpair to transfer reload readiness, daemon parent/child synchronization, cleanup via `atexit`, and aggregate-only mode changing kernel registration/listener behavior. `extract_type` must parse network-originated formatted events correctly for plugin routing.

## Test Signals
There is no direct daemon main unit test. Integration/system tests should cover foreground/background startup, no-fork mode, aggregate-only remote logging, SIGHUP reload, USR1 rotation, USR2 resume, SIGCONT state dump, netlink event filtering, pidfile cleanup, and listener startup failure.
