<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/event.h -->
# sources/security-integrity/audit-userspace/src/libev/event.h

**Purpose**
This is the libev-provided libevent compatibility header used by audit-userspace code that expects classic libevent names. It exposes only core event, timer, signal, and base-loop APIs and maps many names directly onto libev concepts.

**Important APIs, Types, And Functions**
The central type is `struct event`, which embeds a union of `ev_io` and `ev_signal` plus an `ev_timer`. Compatibility fields track `ev_base`, callback, fd, priority, result, flags, and requested event mask. It defines libevent-style helpers such as `event_set`, `event_add`, `event_del`, `event_pending`, `event_once`, `event_loop`, `event_dispatch`, `event_base_new`, `event_base_loop`, and `event_base_once`. Macros alias `EVLOOP_NONBLOCK`, `EVLOOP_ONESHOT`, `EV_TIMEOUT`, `EV_PERSIST`, `EVENT_FD`, and timer/signal helper families.

**Control Flow**
The header declares the API surface; implementation lives in the accompanying libev compatibility source. Callers initialize a base or use the default loop, configure an event object, add it with an optional timeout, and let libev dispatch callbacks.

**State And Persistence**
All state is in memory inside `struct event` and the selected `event_base`; there is no durable persistence. `EVLIST_INIT`, `EVLIST_INSERTED`, `EVLIST_TIMEOUT`, and related flags model lifecycle state.

**Dependencies And Integration Points**
It includes `ev.h` or the configured `EV_H`, plus `time.h`/`sys/time.h` for `timeval`. Audit daemon tests and runtime pieces can use libevent spelling while linking libev.

**Risks**
Only core events are supported; edge-triggered `EV_ET` is a no-op and `event_base_priority_init` has a suspicious `fd` parameter name, reflecting compatibility rather than full libevent parity. Code relying on less-common libevent features may compile but behave differently if only macros exist.

**Test Signals**
Coverage is indirect through auditd event tests linked against `src/libev/libev.la`, especially `format_event_test` in this work item.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/event.h -->
