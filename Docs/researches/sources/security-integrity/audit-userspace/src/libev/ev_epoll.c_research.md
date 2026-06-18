# sources/security-integrity/audit-userspace/src/libev/ev_epoll.c

Purpose: implements the Linux epoll backend for libev fd readiness. It maps libev `EV_READ`/`EV_WRITE` interest to epoll interest, handles epoll-specific kernel quirks, and supplies backend hooks consumed by `ev.c`.

Important APIs/functions: internal hooks are `epoll_init`, `epoll_modify`, `epoll_poll`, `epoll_destroy`, and `epoll_fork`; helper `epoll_epoll_create` uses `epoll_create1(EPOLL_CLOEXEC)` when available or falls back to `epoll_create` plus `FD_CLOEXEC`. State uses `backend_fd`, `epoll_events`, `epoll_eventmax`, `epoll_eperms`, `epoll_epermcnt`, and `ANFD` fields `emask` and `egen`.

Control flow: `epoll_init` creates the epoll fd, installs `backend_modify`/`backend_poll`, and allocates an initial event array. `epoll_modify` ignores pure deletes optimistically, adds or modifies active fds, stores fd plus generation in `data.u64`, handles `ENOENT`/`EEXIST` races, treats `EPERM` as an always-ready fd by placing it in `epoll_eperms`, and kills invalid fds after hard errors. `epoll_poll` calls `epoll_wait`, validates generation counters, repairs interest masks for spurious events, feeds fd events, grows the receive array when full, and synthesizes events for `EPERM` fds.

State and persistence: the backend persists kernel registration in the epoll instance and mirrors it in `anfds[fd].emask`. Generation counters prevent stale events from closed/reused descriptors from being accepted. The `epoll_eperms` array persists fds epoll cannot monitor and is compacted when they no longer need synthetic events.

Dependencies and integration: requires `<sys/epoll.h>` and libev core helpers/macros from `ev.c`. It is included into `ev.c` under `EV_USE_EPOLL` and is also used by the linux AIO backend as its fallback and wakeup path.

Risks: delete elision improves common performance but requires spurious-event repair logic. Epoll behavior across `fork`, descriptor duplication, regular files, and older kernels is explicitly fragile. `EPERM` fds are treated as always ready, which can spin if callers keep unsupported fds active. Backend recreation after generation mismatch sets `postfork |= 2`, so fork/rearm paths must be tested.

Test signals: run fd readiness tests on pipes/sockets, close/reuse watched fds, watch unsupported fds that return `EPERM`, force event-array growth with many ready fds, and verify `ev_loop_fork` rebuilds registrations.
