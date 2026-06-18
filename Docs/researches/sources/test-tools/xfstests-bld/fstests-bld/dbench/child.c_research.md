# sources/test-tools/xfstests-bld/fstests-bld/dbench/child.c

Purpose: implements dbench/tbench child workload execution, parsing NetBench-style load files and dispatching operations to backend `nb_*` functions.

Important APIs and functions: static timing helpers `nb_target_rate`, `nb_time_reset`, `nb_time_delay`, `finish_op`, dispatch helper `child_op`, and exported `child_run(struct child_struct *child0, const char *loadfile)`.

Control flow: initializes client names, allocates token buffers, opens the load file, loops over workload lines forever until `child->done`, normalizes paths, tokenizes fields, validates status tokens, maps `client1` to per-client names, rate-limits or time-aligns operations, and dispatches commands such as `NTCreateX`, `Rename`, `Unlink`, `Deltree`, `Mkdir`, `ReadX`, `WriteX`, and `Flush`.

State and persistence: mutates shared `child_struct` fields including line count, bytes, timing, latency stats, cleanup flags, and per-operation counters. Backend operations mutate filesystem or socket state.

Dependencies and integration: included in both dbench and tbench builds with backend implementations from `fileio.c` or `sockio.c`. Uses global `options`.

Risks: fixed token buffer sizes and line length can truncate malformed workloads. Uses `goto again` for infinite replay and `goto done` for termination. Allocated token buffers are not freed before process exit.

Test signals: children execute workload lines, update operation latency counters, respect target rate/timestamps, and perform cleanup when stopped.
