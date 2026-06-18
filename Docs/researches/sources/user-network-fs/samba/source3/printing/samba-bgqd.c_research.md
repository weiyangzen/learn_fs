# sources/user-network-fs/samba/source3/printing/samba-bgqd.c

## Purpose

`samba-bgqd.c` is the executable entry point for Samba’s background print queue daemon. It parses daemon options, creates a singleton PID file, initializes global messaging/session/locking state, registers print queue handlers, reports readiness, watches its parent, and runs the tevent loop.

## Important APIs, Types, and Functions

- `watch_handler()` marks the daemon done when the parent-watch fd becomes readable.
- `bgqd_sig_term_handler()` marks the daemon done on SIGTERM.
- `ready_signal_filter()` replies to `MSG_DAEMON_READY_FD` by writing this process PID to a passed fd.
- `samba_bgqd_pidfile_create()` creates or races for the daemon PID file and forwards readiness fds to an existing daemon if needed.
- `main()` owns full daemon initialization and event loop.

## Control Flow

`main()` preserves fd parameters through `closefrom_except_fd_params()`, initializes Samba command-line parsing, optionally daemonizes, blocks SIGPIPE, initializes locale and core dumps, obtains the global messaging context and event context, and creates the singleton PID file. If a parent-watch fd was provided, it registers an async read that exits the loop when the parent dies. It initializes guest and system session info with winbind temporarily disabled, installs SIGTERM handling, registers background queue handlers through `register_printing_bq_handlers()`, initializes locking, reports daemon readiness, and loops on `tevent_loop_once()` until `done` is set.

When PID-file creation finds an existing daemon, a new instance sends the ready fd to the existing process using `MSG_DAEMON_READY_FD` and exits with `EAGAIN`. The existing process listens with a filtered messaging read and writes its PID to satisfy the parent readiness wait.

## State and Persistence

Runtime state is held in talloc objects under the stack frame: messaging context, event context, signal handlers, watch request, and `bq_state`. Persistent state is the PID file under `lp_pid_directory()`.

## Dependencies and Integration Points

The daemon depends on Samba command-line/daemon helpers, tevent, messaging, pidfile utilities, async fd waits, security session initialization, winbind toggles, locking initialization, global contexts, and `queue_process.c` handler registration. It is spawned by `start_background_queue()`.

## Risks and Edge Cases

- Singleton races are handled through PID file and fd passing; failures in messaging fd transfer can cause parent readiness timeouts.
- `ready_signal_fd` must be closed after successful readiness reporting to avoid fd leaks.
- The daemon exits on any `tevent_loop_once()` error, so handler errors can terminate background print processing.
- Initialization order matters: messaging must exist before PID race handling, and session info must exist before print queue handlers run.

## Test Signals

Tests should spawn two daemons to exercise PID-file race behavior, verify ready fd reporting, verify parent-watch exit, SIGTERM shutdown, failure paths for missing messaging/session/locking setup, and successful registration of queue handlers.
