# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_subr.c

## Purpose
Provides the core sockfs support machinery: accept queues, blocking waits, signals, mblk/uio copying, receive queue management, ioctl/option common handling, TPI fallback, and kernel receive callbacks.

## Main Behavior
- Accept queue helpers dequeue, flush, and destroy pending or deferred child sockets.
- Connect and send wait helpers sleep on condition variables, honor nonblocking flags, timeouts, fallback, close, and signal interruption.
- `socket_sendsig()` sends `SIGPOLL`/`SIGURG` to process or process group targets in the socket zone.
- `socopyinuio()` copies user data into mblk chains with protocol write offset/tail reservations; `socopyoutuio()` copies mblk data back to uio.
- Receive queue helpers merge mblk chains, prepend partially read data, maintain `so_rcv_queued`, preserve `b_next` message boundaries, and coordinate flow-control release.
- `so_dequeue_msg()` is the main queued receive engine, handling peek, truncation, OOB marks, timers, blocking waits, sodirect/UIOA state, control/data splitting, and flow-control transitions.
- OOB helpers manage urgent-data state, mark behavior, inline delivery, and non-inline `MSG_OOB` reads.
- `socket_sonode_create()` allocates sonodes from `socket_cache`, validates upcall/downcall versions, assigns defaults, and sets protocol receive thresholds.
- `socket_init_common()` initializes passive children by inheriting listener state or active sockets by attaching automatic filters, creating protocol handles, activating downcalls, and applying wildcard protocol options.
- `socket_ioctl_common()` handles nonblocking, async, ownership, at-mark, read-count, and peer credential ioctls.
- `socket_strioc_common()` handles selected STREAM ioctls and otherwise attempts TPI fallback.
- `socket_getopt_common()` handles or validates common `SOL_SOCKET` gets, including `SO_ERROR`, domain/type/acceptconn, timeouts, receive buffer compatibility, send buffer info, and copy-avoid with filters.
- `so_tpi_fallback()` quiesces native sockets, creates TPI sockparams, converts the sonode, migrates queued data and OOB state to STREAMS messages, converts accepted children, flushes accept queues, swaps ops to `sotpi_sonodeops`, and wakes pollers.
- `so_krecv_set()` installs/removes kernel receive callbacks after flushing queued data; `so_krecv_unblock()` releases receive flow control for such callbacks.

## Integration Points
- Used by `sockcommon_sops.c`, TPI code, socket vnode operations, filters, and ksocket consumers.
- Coordinates with `sockparams`, `sotpi_convert_sonode()`, `sotpi_revert_sonode()`, sodirect, STREAMS ioctls, and protocol fallback callbacks.

## Risks and Notes
- Receive queue invariants are subtle: `b_next` separates messages, `b_cont` chains data/control, and `b_prev` stores tail pointers.
- `so_check_flow_control()` intentionally drops `so_lock`; callers must not unlock again.
- Fallback is disabled when filters or kernel receive callbacks are active.
- TPI fallback has a debug integrity check to catch lost state if conversion fails and must revert.
