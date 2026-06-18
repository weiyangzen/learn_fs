# sources/security-integrity/audit-userspace/src/libev/event.c

Purpose: implements a libevent-compatible API on top of libev. It lets code written for older libevent-style `struct event` and `event_base` calls run against the bundled libev core.

Important APIs/functions: exports `event_get_version`, `event_get_method`, `event_init`, `event_base_new`, `event_base_free`, `event_dispatch`, `event_loop`, `event_loopexit`, `event_set`, `event_add`, `event_del`, `event_active`, `event_pending`, `event_base_set`, `event_base_loop`, `event_base_dispatch`, `event_base_loopexit`, `event_once`, `event_base_once`, `event_priority_init`, `event_priority_set`, and `event_get_callback`. Internal callbacks `ev_x_cb_io`, `ev_x_cb_sig`, `ev_x_cb_to`, and `ev_x_once_cb` translate libev revents into libevent callback signatures.

Control flow: `event_init` initializes the current base as the default libev loop on first use or a new loop later when multiplicity is enabled. `event_set` initializes embedded libev io/signal and timer watchers inside `struct event`. `event_add` starts the signal or io watcher and optionally arms the timeout watcher. `event_del` stops all active embedded watchers. Read/write callbacks delete non-persistent events before invoking the user callback; timeout callbacks always delete first. Base loop and dispatch calls delegate to `ev_run`; loopexit schedules an `ev_once` timer that calls `ev_break`.

State and persistence: global `ev_x_cur` stores the current event base. `struct event_base` is an opaque dummy type cast to/from `struct ev_loop`. Each `struct event` persists callback metadata, flags, fd, requested events, priority, result bits, base pointer, and embedded libev watchers. `event_base_once` allocates a small heap wrapper and frees it after the callback.

Dependencies and integration: includes `event.h` or a configured `EV_EVENT_H`, plus `ev.h` through that compatibility header. It depends on libev multiplicity for multiple independent bases; without multiplicity it asserts on multiple base creation. It uses standard `malloc/free` for one-shot compatibility wrappers rather than libev's allocator hook.

Risks: `event_init` and `ev_x_cur` are not thread-safe. The compatibility layer only approximates libevent semantics: priority initialization is a no-op, `event_pending` reports timeout time as current loop time rather than remaining timeout, and only read/write/signal/timer behavior is mapped. Non-persistent io events are deleted before callback, so callback code must re-add if needed. One-shot allocation failure returns `-1`.

Test signals: run libevent-style tests for persistent and non-persistent fd events, signal events, timeout-only events, combined fd+timeout events, `event_once`, `event_base_once`, `event_loopexit`, and multiple bases when `EV_MULTIPLICITY` is enabled.
