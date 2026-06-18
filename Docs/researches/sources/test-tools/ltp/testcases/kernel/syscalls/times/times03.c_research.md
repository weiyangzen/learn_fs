<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/times/times03.c

Purpose: DESCRIPTION Testcase to check the basic functionality of the times() system call. ALGORITHM This testcase checks the values that times(2) system call returns. Start a process, and spend some CPU time by performing a spin in a for-loop. Then use the times() system call, to determine the cpu time/sleep time, and other statistics. 07/2001 John George At least some CPU time must be used in system space. This is achieved by executing the times(2) call for at least 2 secs. This logic makes it independent of the processor speed. Run the test in a child to reset times in case of -i option.

Important APIs/types/functions: includes `sys/types.h`, `sys/times.h`, `errno.h`, `sys/wait.h`, `time.h`, `signal.h`, `stdlib.h`, `tst_test.h`; exercises `time`, `times`; defines `sighandler`, `work`, `generate_utime`, `generate_stime`, `verify_times`, `do_test`, `setup`; uses constants `SIGALRM`.

Control flow centers on `sighandler`, `work`, `generate_utime`, `generate_stime`, `verify_times`, `do_test`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all` into the runner.

State and persistence behavior: Runtime state is per-process CPU tick accounting in `struct tms` plus monotonic elapsed clock ticks.

Dependencies and integration points: Depends on `times(2)`, `sysconf(_SC_CLK_TCK)`, and stable CPU accounting around busy or elapsed work. Direct include dependencies include `sys/types.h`, `sys/times.h`, `errno.h`, `sys/wait.h`, `time.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times03.c -->
