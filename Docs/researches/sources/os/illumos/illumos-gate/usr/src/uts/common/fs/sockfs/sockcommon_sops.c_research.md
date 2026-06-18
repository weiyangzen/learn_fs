# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_sops.c

## Purpose
Implements the generic non-STREAM sonode operations and protocol upcall table used by sockfs native socket modules.

## Main Behavior
- Provides unsupported sonode operations returning `EOPNOTSUPP`.
- `so_bind()`, `so_listen()`, `so_connect()`, `so_accept()`, name, option, shutdown, ioctl, send, receive, and poll paths wrap protocol downcalls with fallback blocking and optional socket filter hooks.
- IPv4/IPv6 bind validation applies historical SunOS compatibility and stricter X/Open checks.
- Send paths support direct `sd_send_uio` or mblk construction via `socopyinuio()`, enforce atomic max packet size, honor send flow control, process OOB, and run outbound filters.
- `so_sendmblk_impl()` sends prebuilt mblk chains, splitting by protocol max packet size and supporting filter-injected output.
- Receive paths use direct protocol receive when available, otherwise dequeue sockfs receive queues, decode TPI control messages, translate options to control messages, set `MSG_EOR`/`MSG_TRUNC`, and handle OOB.
- Poll reports errors, writable state, accept queue readiness, receive data/OOB, `POLLRDHUP`, `POLLHUP`, protocol poll events, and edge-trigger bookkeeping.
- Protocol upcalls update connected/disconnected state, accept new connections, set protocol properties, queue inbound messages, signal OOB, set errors, notify zero-copy completion, and release async-close references.
- Exports `so_sonodeops` and `so_upcalls`.

## Integration Points
- Heavily uses helpers from `sockcommon_subr.c`, notifications from `socknotify.c`, filter APIs from `sockfilter.c`, and protocol downcalls from socket modules.
- Supports ksocket callbacks and sodirect receive acceleration.
- `so_newconn()` feeds the accept queue and handles deferred filter-controlled connections.

## Risks and Notes
- Many operations use `SO_BLOCK_FALLBACK()`/`SO_UNBLOCK_FALLBACK()` so TPI fallback can quiesce active operations safely.
- `so_getsockopt()` emulates successful default `SOL_SOCKET` gets for unsupported protocol options to preserve previous sockfs behavior.
- Close handling may be synchronous or asynchronous; async close relies on a later `so_closed()` upcall to drop the protocol vnode reference.
- Filter injection is tracked with `so_filter_tx` so close waits until injected transmit operations finish.
