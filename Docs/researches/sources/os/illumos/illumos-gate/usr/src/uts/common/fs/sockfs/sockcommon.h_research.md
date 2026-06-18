# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.h

## Purpose
Internal sockfs header declaring common socket wrappers, sonode operations, protocol upcalls, queue helpers, notification helpers, lifecycle routines, and timer macros.

## Main Behavior
- Declares `socket_create()`, `socket_newconn()`, and common `socket_*` operation wrappers.
- Defines `SOCKET_TIMER_CANCEL()` and `SOCKET_TIMER_START()` for receive push timer management under `so_lock`.
- Declares unsupported sonode ops and the generic `so_*` operations implemented in `sockcommon_sops.c`.
- Declares protocol upcalls such as `so_newconn()`, `so_connected()`, `so_queue_msg()`, `so_set_prop()`, and `so_txq_full()`.
- Declares accept queue, connect wait, send wait, signal, receive queue, uio/mblk copy, OOB, ioctl, option, fallback, zcopy, and notification helpers.
- Exposes `so_sonodeops` and `so_upcalls`.
- Defines socket signal event bits for write, read, and urgent notifications.

## Integration Points
- Included by the common sockfs implementation, socket filters, TPI fallback code, and socket vnode operations.
- Bridges `sys/socket_proto.h` downcall/upcall interfaces to internal `sonode` state management.

## Risks and Notes
- Several timer macros deliberately drop and reacquire `so_lock`, so callers must respect their locking contract.
- The declarations show the split between public wrapper APIs (`socket_*`), sonode ops (`so_*`), and protocol callbacks/upcalls.
