# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.c

## Purpose
Implements the common sockfs public wrapper layer and sonode lifecycle routines shared by system-call sockets and kernel sockets.

## Main Behavior
- `socket_create()` resolves a `sockparams` entry by family/type/protocol, optionally creates ephemeral entries by device or module, invokes the socket module create function, initializes the sonode, and opens the vnode reference.
- `socket_newconn()` creates a child sonode for passive opens using the parent socket parameters and protocol lower handle.
- Wrapper functions delegate bind/listen/accept/connect/name/options/send/recv/ioctl/poll/shutdown through the active `sonodeops_t`.
- `socket_listen()` normalizes negative backlog to zero and applies BSD-style backlog inflation.
- `socket_connect()` treats `AF_UNSPEC` as disconnect/unconnect and maps `EHOSTUNREACH` to `ENETUNREACH` for XPG callers.
- `socket_sendmsg()` and `socket_recvmsg()` handle uio cache flags, partial-transfer errno normalization, and SIGPIPE on `EPIPE`.
- `sonode_constructor()` allocates and initializes the vnode, queues, locks, condition variables, filter fields, and receive/send state.
- `sonode_init()` resets per-instance state, vnode identity, protocol fields, socket options, poll state, callbacks, and zone ownership.
- `sonode_fini()` cancels timers, wakes pollers, tears down direct I/O and filters, releases peer credentials, invalidates the vnode, and asserts queues are drained.

## Integration Points
- Calls into `sockparams`, socket modules, `sonodeops_t`, vnode operations, sockfilter cleanup, and sodirect setup/teardown.
- Provides the stable `socket_*` interface declared in `sockcommon.h`.
- Works with both native non-STREAM sockfs sockets and TPI fallback sockets.

## Risks and Notes
- Creation carefully preserves original lookup errors when fallback lookup by wildcard protocol changes errno.
- `socket_destroy()` invalidates and releases the vnode; actual resource destruction is completed by vnode inactive paths.
- The constructor/destructor include many assertions that queue/filter state is empty when cache objects are destroyed.
