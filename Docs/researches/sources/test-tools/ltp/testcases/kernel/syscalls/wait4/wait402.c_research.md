<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait402.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait402.c

Purpose: verifies `wait4()` returns `ECHILD` when asked to wait for an invalid pid larger than the kernel `pid_max`.

Important APIs/types/functions: `setup()` reads `PATH_KERN_PID_MAX`; `run()` calls `wait4(pid_max + 1, &status, 0, &rusage)` through `TST_EXP_FAIL2`.

Control flow/state: no children are created. The test depends on current kernel pid namespace limits from procfs.

Dependencies/integration: LTP `SAFE_FILE_SCANF` and `PATH_KERN_PID_MAX` constants.

Risks/test signals: a stale or namespaced pid_max read would affect the invalid-pid choice. Expected failure is `ECHILD`, not `ESRCH`, for this out-of-range positive pid.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait402.c -->
