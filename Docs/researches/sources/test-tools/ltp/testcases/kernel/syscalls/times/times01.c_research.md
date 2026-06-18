<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/times/times01.c

Purpose: This is a Phase I test for the times(2) system call. It is intended to provide a limited exposure of the system call.

Important APIs/types/functions: includes `sys/times.h`, `errno.h`, `tst_test.h`; exercises `times`; defines `verify_times`.

Control flow centers on `verify_times`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is per-process CPU tick accounting in `struct tms` plus monotonic elapsed clock ticks.

Dependencies and integration points: Depends on `times(2)`, `sysconf(_SC_CLK_TCK)`, and stable CPU accounting around busy or elapsed work. Direct include dependencies include `sys/times.h`, `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/times/times01.c -->
