<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.c

Purpose:  Test ru_maxrss behaviors in struct rusage. This test program is backported from upstream commit: 1f10206cf8e9, which fills ru_maxrss value in struct rusage according to rss hiwater mark. To make sure this feature works correctly, a series of tests are executed in this program.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `tst_test.h`, `getrusage03.h`; defines `inherit_fork1`, `inherit_fork2`, `grandchild_maxrss`, `zombie`, `sig_ign`, `inherit_exec`, `run`; uses LTP safe helpers such as `SAFE_EXECLP`, `SAFE_FORK`, `SAFE_GETRUSAGE`, `SAFE_SIGNAL`, `SAFE_WAIT`.

Control flow centers on `inherit_fork1`, `inherit_fork2`, `grandchild_maxrss`, `zombie`, `sig_ign`, `inherit_exec`, `run`. The `struct tst_test` registration wires `.forks_child`, `.test`, `.tcnt`, `.caps` into the LTP runner.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `stdlib.h`, `stdio.h`, `tst_test.h`, `getrusage03.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_CAP`, `TST_CAP_REQ`, `TST_PROCESS_EXIT_WAIT`, `TST_PROCESS_STATE_WAIT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.c -->
