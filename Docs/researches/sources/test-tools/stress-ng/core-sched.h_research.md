# sources/test-tools/stress-ng/core-sched.h

Purpose: declares scheduler policy metadata and the public helpers for parsing and applying scheduler settings.

Important APIs/types/functions: `stress_sched_types_t` records numeric policy, user-facing name, macro name, and whether `sched_getscheduler` checks are expected. Public declarations expose the scheduler table/length, name lookup, setter, parser, settings applier, and sched_ext ops reader.

Control flow: header feature guards define syscall availability flags for `sched_getattr` and `sched_setattr`, and provide `SCHED_EXT` as 7 on Linux when headers do not define it.

State and persistence: no state in the header. Functions declared here can mutate process scheduler state at runtime.

Dependencies/integration: includes `core-attribute.h`, Linux sched/syscall headers where available, and uses `pid_t`, `bool`, and `ssize_t` from the common environment.

Risks: fallback definition of `SCHED_EXT` is numeric and Linux-specific; callers still need runtime error handling. Any new scheduler policy should be added to both the implementation table and tests.

Test signals: compile with old and new Linux headers, non-Linux platforms, and callers using `stress_sched_types_length` for option help.
