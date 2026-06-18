# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socknotify.c

## Purpose
Centralizes socket state notifications, wakeups, signals, poll events, ksocket callbacks, and filter event notifications.

## Main Behavior
- All exported notification functions require `so_lock` on entry and drop it before returning.
- `so_notify_connected()` wakes connect waiters and reports writable/connected state.
- Disconnecting, disconnected, EOF, and shutdown notifications send final read/write wakeups only once using `SS_SENTLASTREADSIG` and `SS_SENTLASTWRITESIG`.
- Writable and data notifications wake blocked senders/readers, issue kernel socket callbacks or user poll/signal notifications, and clear edge-trigger poll state.
- Error notifications wake both read and write waiters and report poll input/output readiness.
- OOB notifications handle urgent signal, OOB data readiness, inline OOB read readiness, and sodirect cleanup.
- New connection notifications wake accept waiters and pollers.
- Helper functions `i_so_notify_last_rx()` and `i_so_notify_last_tx()` consolidate final read/write notification state.

## Integration Points
- Called from protocol upcalls in `sockcommon_sops.c`, queue/timer paths in `sockcommon_subr.c`, and shutdown/close paths.
- Invokes `socket_sendsig()`, `pollwakeup()`, `KSOCKET_CALLBACK()`, sodirect cleanup, and `sof_sonode_notify_filters()`.

## Risks and Notes
- The locking convention is unusual but explicit: callers must not expect `so_lock` to remain held.
- `SO_WAKEUP_READER` uses `cv_signal` because only one read waiter is allowed; writers use broadcast.
- Filter notifications are emitted after releasing `so_lock`.
