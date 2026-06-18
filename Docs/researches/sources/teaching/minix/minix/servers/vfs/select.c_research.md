# File Research: sources/teaching/minix/minix/servers/vfs/select.c

Implements `select(2)` over regular files, pipes/FIFOs, character devices, and socket devices.

Key behavior:
- `do_select` validates `nfds`, allocates a `selectentry`, copies fd sets, validates timeout, maps selected fds to filps and file types, issues readiness checks, returns immediately when ready/error/poll, or suspends with an optional timer.
- Regular files are always ready.
- Pipes are checked synchronously with `pipe_check`; blocking pipe select records wanted operations in `filp_pipe_select_ops`.
- Character and socket devices use asynchronous driver select requests through `cdev_select` and `sdev_select`.
- `select_filter` manages filp-level select flags for pending, busy, blocked, and update state.
- `copy_fdsets` copies only the user-requested fd-set size in and out.
- `select_cancel_all` and `select_cancel_filp` tear down per-call and per-filp selector state, marking in-flight driver queries stale when needed.
- `select_return` copies ready sets and revives the blocked process.
- `select_timeout_check` returns when timeout expires, or converts the request to nonblocking if async replies are still deferred.
- `select_unsuspend_by_endpt` cleans up selectors when a process or driver exits, marking affected fds readable/writable so later I/O reports errors.

Reply handling:
- `select_cdev_reply1` and `select_sdev_reply1` process initial poll replies and restart deferred filps.
- `select_cdev_reply2` and `select_sdev_reply2` process later readiness notifications.
- `select_reply2`, `filp_status`, and `restart_proc` propagate status to all waiting select calls that share a filp/device.

Notable implementation details:
- The module intentionally uses minimal locking so driver replies can be processed without blocking.
- Per-call `selectentry` state and per-filp select state are separate, allowing multiple processes or fds to share one in-flight select query.
- `select_dump` provides detailed runtime diagnostics for active select entries and underlying device state.
