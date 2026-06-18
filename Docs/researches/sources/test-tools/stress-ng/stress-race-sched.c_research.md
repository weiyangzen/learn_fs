# sources/test-tools/stress-ng/stress-race-sched.c research

Purpose: implements `race-sched`, a scheduler/OS stressor that forks short-lived children while racing CPU affinity and non-realtime scheduler policy changes across the process tree.

Important APIs, types, and functions: `stress_race_sched_child_t` and `stress_race_sched_list_t` maintain active and recycled child records. Method tables select CPU movement patterns: all, next, previous, random, random increment, syncnext, and syncprev. `stress_race_sched_setaffinity()` wraps `sched_setaffinity` plus verification via `sched_getaffinity`; `stress_race_sched_setscheduler()` randomly chooses normal policies and verifies with `sched_getscheduler`.

Control flow: `stress_race_sched()` runs `stress_race_sched_child()` inside `stress_oomable_child`. The child obtains eligible CPUs, then loops setting its own affinity, forking until a child limit or low-memory condition, and applying random combinations of yield, affinity changes, scheduler changes, and list-wide exercise passes in both parent and children. It reaps old children opportunistically and drains all remaining children on exit.

State and persistence: global process-local child lists and CPU arrays are transient. No files or durable scheduler settings persist after children exit.

Dependencies and integration: gated by `sched_setaffinity`, POSIX/Linux scheduling, normal scheduler policy constants, and `sched_setscheduler`. Uses stress-ng affinity helpers, OOM avoidance, randomization, and oomable wrapper. Classified as scheduler and OS.

Risks: the code intentionally races process lifetime against scheduler operations, so `ESRCH` is tolerated but other errors fail. Child list management must avoid leaks during fork failure and low-memory reaping. CPU index zero is skipped by the `cpu_idx > 0` condition, which may reduce coverage on single-CPU systems.

Test signals: bogo ops per fork/exercise cycle, max fork depth through behavior, affinity/scheduler failure logs, OOM-avoidance reaping, and clean free of child lists/CPU arrays.
