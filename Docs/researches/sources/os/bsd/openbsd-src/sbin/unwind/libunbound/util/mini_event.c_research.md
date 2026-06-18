# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.c

Minimal libevent-compatible backend using `select(2)`, compiled when `USE_MINI_EVENT` is defined and `USE_WINSOCK` is not.

Key functions:
- `mini_ev_cmp(...)`: comparator for timeout tree entries, ordered by absolute timeout then pointer address for uniqueness.
- `event_init(time_secs, time_tv)`: allocates an `event_base`, initializes current time, creates timeout rbtree, allocates fd and signal arrays, initializes fd sets.
- `event_get_version()`: returns `mini-event-<PACKAGE_VERSION>`.
- `event_get_method()`: returns `"select"`.
- `handle_timeouts(...)`: fires expired timeout callbacks from the rbtree and computes wait duration for the next timeout.
- `handle_select(...)`: copies fd sets, calls `select`, updates current time, and dispatches ready read/write callbacks.
- `event_base_dispatch(...)`: main loop; processes timeouts then select events until `need_to_exit`.
- `event_base_loopexit(...)`: sets exit flag.
- `event_base_free(...)`: frees base-owned arrays/tree/base.
- `event_set(...)`: initializes a single event structure and validates callback with `fptr_ok`.
- `event_base_set(...)`: associates event with base.
- `event_add(...)`: activates fd and/or timeout event, updates fd sets and max fd.
- `event_del(...)`: removes fd and/or timeout event and adjusts max fd.
- `signal_add(...)` / `signal_del(...)`: basic single-event-per-signal handling through `signal(2)` and a global `signal_base`.
- Non-mini-event fallback defines a stub `mini_ev_cmp` returning 0 for non-Winsock builds.

Important constraints:
- One event per fd.
- One handler per signal.
- Limited by `MAX_FDS` and `FD_SETSIZE`.
- Signal handling is global through `signal_base`, so multiple event bases cannot independently own signal dispatch.
- Callback pointers are checked against the function-pointer whitelist before invocation.

Dependencies:
- `util/mini_event.h`, `util/fptr_wlist.h`, rbtree support, `gettimeofday`, `select`, `signal`.

Research notes:
- Despite header comments saying second-level timeout accuracy, implementation stores and compares microseconds.
- The implementation intentionally covers only the subset of libevent API needed by this codebase.
