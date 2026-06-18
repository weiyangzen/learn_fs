<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid04.c

Purpose: negative `waitpid()` errno test for no children, non-child pid, invalid flags, and `INT_MIN` process-group edge case.

Important APIs/types/functions: `testcase_list[]` holds pid, flags, and expected errno: `ECHILD`, `ECHILD`, `EINVAL`, and `ESRCH`. `run()` calls `TST_EXP_FAIL2(waitpid(...))` for each row.

Control flow/state: no child processes are created; every call should fail from syscall validation or child lookup.

Dependencies/integration: minimal LTP harness with `<sys/wait.h>` and signal constants.

Risks/test signals: the `INT_MIN` case protects the same negation edge as wait4. Wrong errno mapping is the principal failure mode.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid04.c -->
