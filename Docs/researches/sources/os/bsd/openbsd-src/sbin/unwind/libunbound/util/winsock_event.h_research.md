# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/winsock_event.h

## Purpose
Declares Unbound's Windows WinSock event API and maps common libevent symbols onto the local `winsockevent_*` implementation when `USE_WINSOCK` is enabled.

## Main Contents
- Defines libevent-compatible event flags: `EV_TIMEOUT`, `EV_READ`, `EV_WRITE`, `EV_SIGNAL`, and `EV_PERSIST`.
- Renames event APIs such as `event_init`, `event_add`, `event_del`, and `signal_add` to WinSock-specific names to avoid symbol collision.
- Defines fixed limits: `MAX_SIG` for signals and `WSK_MAX_ITEMS` for waitable WinSock objects.
- Declares `struct event_base`, which stores timeout tree, active item array, signal table, time pointers, TCP sticky counters, and current wait handles.
- Declares `struct event`, which stores public event metadata plus WinSock-private fields such as array index, `WSAEVENT`, TCP sticky state, signal-event flag, and callback processing marker.

## Public API
- Event base lifecycle: `event_init`, `event_base_dispatch`, `event_base_loopexit`, `event_base_free`.
- Event setup and registration: `event_set`, `event_base_set`, `event_add`, `event_del`.
- Timer aliases: `evtimer_add`, `evtimer_del`.
- Signal support: `signal_set`, `signal_add`, `signal_del`.
- WinSock-specific helpers: `winsock_tcp_wouldblock`, `winsock_register_wsaevent`, `winsock_unregister_wsaevent`.
- `mini_ev_cmp` is exposed for timeout rbtree ordering.

## Design Notes
The header documents the main portability problem: Windows socket readiness behaves differently from Unix readiness, and TCP streams require remembered event bits until the application reports `WSAEWOULDBLOCK`. It also records practical Windows constraints: no generic file-descriptor waits, limited wait handles, non-small socket numbers, and TCP I/O should use `recv`/`send`.

## Dependencies and Integration
Only active under `USE_WINSOCK`. It depends on Unbound's `rbtree.h` and WinSock types such as `WSAEVENT`. Consumers include `winsock_event.c` and other Unbound code compiled against event/libevent-like APIs.

## Notable Constraints
The structures are not opaque in this header, so internal implementation details are visible to callers. That matches the local libevent compatibility style but makes ABI/layout changes more exposed.
