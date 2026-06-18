<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-alarm.c -->
# sources/test-tools/stress-ng/stress-alarm.c

Purpose: `stress-alarm.c` implements the `alarm` stressor. It stresses `alarm()`, `sleep()`, signal interruption, fork/reap behavior, and optional semantic verification for large, zero, and random timeout values.

Important APIs/types/functions: test-result bits are split into sleep and alarm masks for `INT_MAX`, zero, and random durations. `stress_alarm_stress_bogo_inc()` blocks `SIGUSR1` around `stress_bogo_inc()` so the parent termination signal cannot interrupt the counter update. `stress_alarm()` is the main stressor entry point and installs a parent `SIGALRM` ignore handler.

Control flow: after the sync barrier, the stressor forks a child. The child installs `SIGUSR1` as an exit handler, enables failure-injection behavior, and loops over alarm/sleep scenarios: cancel pending alarms, schedule `alarm(INT_MAX)`, reschedule it to check returned remaining time, call `sleep(INT_MAX)` expecting interruption, test `alarm(0)` and `sleep(0)`, and test a random alarm/sleep pair. It records mismatches in an exit-status bitmask. The parent repeatedly sends `SIGALRM` to interrupt the child, then sends `SIGUSR1`, waits, and, when verify is enabled, reports the bitmask categories.

State and persistence behavior: the stressor stores no persistent files or shared memory. State is the forked child, process signal dispositions, the child's exit-code mask, and the bogo counter. `stress_make_it_fail_set()` is child-local.

Dependencies and integration points: it uses `core-signal.h`, stress-ng fork retry logic, sync barriers, process-state transitions, random delay generation, `shim_kill`, `shim_nanosleep_uint64`, `shim_sched_yield`, and optional verify mode. It is registered as `CLASS_SIGNAL | CLASS_INTERRUPT | CLASS_OS` with `VERIFY_OPTIONAL`.

Risks: using an exit status as a bitmask limits result width, though the current masks fit. Parent kill loops depend on `args->time_end` and `stress_continue(args)`; changes to time accounting could leave short runs with weak coverage. Signal handler interactions are central, so global signal changes elsewhere can break assumptions.

Test signals: verify-mode failures list exact failing cases such as `sleep(INT_MAX)`, `alarm(0)`, or `alarm($RANDOM)`. Regression tests should cover fork retry paths, immediate stop, signal delivery races, and platforms with different `sleep()` interruption semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-alarm.c -->
