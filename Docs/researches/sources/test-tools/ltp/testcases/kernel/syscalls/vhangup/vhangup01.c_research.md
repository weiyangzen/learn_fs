<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup01.c

Purpose: verifies `vhangup()` fails with `EPERM` when called by a non-root user.

Important APIs/types/functions: `setup()` resolves the `nobody` UID. `run()` forks; the child calls `setreuid(nobody, nobody)`, invokes `tst_syscall(__NR_vhangup)`, and checks return `-1` with `TST_ERR == EPERM`.

Control flow/state: privilege drop happens only in the child, while the root parent waits. No persistent state is created.

Dependencies/integration: requires root and LTP raw syscall wrapper because libc exposure can vary. `.forks_child = 1` isolates credential changes.

Risks/test signals: systems without a `nobody` account fail setup. Runtime failures indicate changed privilege checks or wrong errno for unprivileged virtual terminal hangup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup01.c -->
