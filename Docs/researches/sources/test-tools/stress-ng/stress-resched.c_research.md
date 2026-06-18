# sources/test-tools/stress-ng/stress-resched.c

Purpose: implements `resched`, a scheduler stressor that spawns children at a range of nice levels and has them repeatedly yield while optionally cycling normal scheduling policies.

Important APIs/types/functions: `stress_resched_info` is `CLASS_SCHEDULER | CLASS_OS` and `VERIFY_ALWAYS`. `stress_resched_usr1_handler()` lets children signal parent shutdown on scheduler verification failure. `stress_resched_child()` performs yield loops, `sched_setscheduler()`, `sched_getscheduler()`, and `nice(1)` progression. `stress_resched_spawn()` owns child creation for a slot.

Control flow: `stress_resched()` derives the maximum nice slot from `RLIMIT_NICE`, maps a shared PID table and shared yield counters, installs a SIGUSR1 handler, synchronizes, then starts one child per nice slot. The parent waits for children; when one exits it respawns that slot unless a failure or stop condition occurs. Children loop from their slot niceness up to the maximum, performing 1024 yield batches and optional scheduler policy switches per level.

State and persistence: state is shared anonymous PID/counter memory and child processes. On shutdown the parent kills/waits all children, prints per-priority yield percentages for instance zero, unmaps shared memory, and returns failure if children failed.

Dependencies and integration points: requires `nice()`; richer policy coverage depends on POSIX/Linux scheduling and `sched_setscheduler()`. It uses stress-ng PID sync, kill/wait helpers, signal handling, scheduling settings, and bogo counters.

Risks and test signals: scheduler calls may fail under low privileges or platform policy restrictions. Verification checks that `sched_getscheduler()` matches successfully set normal policies. Useful signals include balanced child respawn, yield distribution debug output, no orphaned children, and `EXIT_NOT_IMPLEMENTED` path when nice support is absent.
