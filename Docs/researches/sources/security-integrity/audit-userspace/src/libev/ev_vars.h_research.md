# sources/security-integrity/audit-userspace/src/libev/ev_vars.h

Purpose: declares the complete set of fields that make up libev loop state. It is included by `ev.c` with different `VAR` definitions to either populate `struct ev_loop` in multiplicity mode or define static globals in single-loop mode.

Important APIs/types: this is not a public API, but it enumerates critical loop members: clocks (`now_floor`, `mn_now`, `rtmn_diff`), reverse-feed and pending queues, backend identity/function pointers, fd watcher arrays, wakeup pipe state, backend-specific storage for select/poll/epoll/linuxaio/iouring/kqueue/port/iocp, fd-change queues, timer and periodic heaps, idle/prepare/check/fork/cleanup/async watcher arrays, inotify/signalfd/timerfd state, original flags, loop counters, userdata, and advanced callbacks.

Control flow: the file is macro-expanded by its includer. Each `VARx(type, name)` expands through `VAR(name, type name)`, while array declarations use `VAR` directly. Conditional blocks mirror feature macros so disabled watcher/backend fields do not exist unless `EV_GENWRAP` is generating wrappers.

State and persistence: every declaration here is persistent event-loop state owned by libev for the lifetime of a loop. The fields store heap allocations, kernel descriptor numbers, callback pointers, counters, atomic flags, and backend-private arrays that are initialized in `loop_init`, mutated throughout `ev_run` and watcher operations, and released in `ev_loop_destroy`.

Dependencies and integration: tightly coupled to `ev.c` internal typedefs (`W`, `ANFD`, `ANPENDING`, `ANHE`, `ANFS`) and platform/backend types such as `struct pollfd`, `struct epoll_event`, `aio_context_t`, `struct iocb`, `sigset_t`, and `HANDLE`. `ev_wrap.h` must stay synchronized with this file.

Risks: adding/removing/reordering fields changes `struct ev_loop` layout and can break binary compatibility for consumers compiled with different feature macros. Conditional fields must match backend code and destroy/fork logic exactly. Wrapper generation drift between this file and `ev_wrap.h` causes compile failures or incorrect macro access.

Test signals: compile with multiplicity on/off and a matrix of backend feature macros, verify `ev_wrap.h` regeneration is clean, and run loop lifecycle tests under each backend to catch missing initialization or cleanup for a declared field.
