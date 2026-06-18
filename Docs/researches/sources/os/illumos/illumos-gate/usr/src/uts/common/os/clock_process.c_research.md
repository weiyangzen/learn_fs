# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_process.c

This file registers a read-only `CLOCK_PROCESS_CPUTIME_ID` backend. It reports CPU time consumed by the current process using existing microstate accounting.

Core behavior:
- `clock_process_gettime()` locks `curproc->p_lock`, sums `mstate_aggr_state(p, LMS_USER)` and `mstate_aggr_state(p, LMS_SYSTEM)`, and converts the result to `timespec_t`.
- `LMS_SYSTEM` aggregation includes `LMS_TRAP`, matching `/proc` status behavior.
- `clock_process_getres()` reports `cyclic_getres()`, matching the thread CPU-time backend’s resolution choice.
- `clock_process_settime()` and all timer operations return `EINVAL`; interval timers are not implemented for this clock.
- `clock_process_init()` fills the backend dispatch table and registers `CLOCK_PROCESS_CPUTIME_ID`.

Important invariants:
- The clock is scoped only to the calling process.
- Timer callbacks/default signal metadata are filled for backend completeness but timer creation is deliberately unsupported.
- `p_lock` is required while aggregating process microstate time.
