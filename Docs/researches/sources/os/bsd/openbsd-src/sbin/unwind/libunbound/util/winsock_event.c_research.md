# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.c

## Purpose
Implements Unbound's Windows-specific event loop adapter when `USE_WINSOCK` is enabled. It provides a small libevent-like API over WinSock `WSAWaitForMultipleEvents`, plus special handling for TCP readiness because Windows socket events do not behave like Unix level-triggered readiness in practice.

When `USE_WINSOCK` is not defined, the file only exports `winsock_unused_symbol` to keep archive tools happy.

## Main Responsibilities
- Creates and destroys `struct event_base` with fixed WinSock wait capacity, timeout rbtree, signal table, and shared time pointers.
- Implements event registration, deletion, dispatch, and loop exit functions compatible with Unbound's event abstraction.
- Converts WinSock network events (`FD_READ`, `FD_WRITE`, `FD_CONNECT`, `FD_ACCEPT`, `FD_CLOSE`) into Unbound event bits (`EV_READ`, `EV_WRITE`, `EV_TIMEOUT`).
- Maintains "sticky" TCP readiness state until callers report `WSAEWOULDBLOCK` through `winsock_tcp_wouldblock`.
- Supports timer-only events through an rbtree sorted by absolute timeout.
- Supports both C signal callbacks and user-provided `WSAEVENT` callbacks.

## Key Functions
- `mini_ev_cmp`: orders events in the timeout rbtree by `ev_timeout`, then pointer address for uniqueness.
- `event_init`: allocates the event base, initializes time, event arrays, rbtree, and signal table.
- `handle_timeouts`: expires due timeout events and calculates the next wait interval.
- `handle_select`: builds the WinSock wait array, waits or sleeps, enumerates socket events, runs callbacks, and updates sticky TCP state.
- `event_base_dispatch`: main loop that alternates timeout processing and WinSock waits until `need_to_exit`.
- `event_add`: registers socket/time events, creates `WSAEVENT`s, calls `WSAEventSelect`, detects TCP/listening sockets, and inserts timeout nodes.
- `event_del`: removes timeout/socket events, compacts the event array, disables `WSAEventSelect`, closes event handles, and clears active wait slots.
- `signal_add` / `signal_del`: simple process-signal callback registration using a single global `signal_base`.
- `winsock_register_wsaevent` / `winsock_unregister_wsaevent`: lets callers add externally owned `WSAEVENT` objects to the same wait loop.

## Control Flow
The dispatch loop first updates wall-clock time, runs all expired timeout callbacks, then waits on currently registered `WSAEVENT`s. If TCP sticky events exist, the wait timeout becomes zero so callbacks are retried until the socket operation reports would-block. During callback processing, `waitfor[]` entries can be zeroed by deletion to avoid invoking callbacks for events removed during another callback.

## Dependencies and Integration
Depends on `util/winsock_event.h`, `util/rbtree`, Unbound logging/assertion helpers, WinSock APIs, and `util/fptr_wlist.h` callback whitelist checks. It is an internal compatibility layer for Unbound code expecting libevent-style functions.

## Notable Constraints and Risks
- WinSock wait limit is fixed at `WSK_MAX_ITEMS` / 64.
- `signal_base` is global, so signal handling is not multi-base safe.
- The code assumes callers report would-block for TCP streams; otherwise sticky readiness may continue to fire.
- `event_base_free` frees the timeout tree container but expects events themselves to be managed elsewhere.
- `event_add` logs WinSock errors but does not always abort registration after failed `WSACreateEvent` or `WSAEventSelect`.
