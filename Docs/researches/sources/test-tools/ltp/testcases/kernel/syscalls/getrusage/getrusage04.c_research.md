<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c

Purpose: getrusage04 - accuracy of getrusage() with RUSAGE_THREAD This program is used for testing the following upstream commit: 761b1d26df542fd5eb348837351e4d2f3bc7bffe. getrusage() returns cpu resource usage with accuracy of 10ms when RUSAGE_THREAD is specified to the argument who. Meanwhile, accuracy is 1ms when RUSAGE_SELF is specified. This bad accuracy of getrusage() caused a big impact on some application which is critical to accuracy of cpu usage. The upstream fix removed casts to clock_t in task_u/stime(), to keep

Important APIs/types/functions: includes `sys/types.h`, `sys/resource.h`, `sys/time.h`, `errno.h`, `stdio.h`, `stdlib.h`, `time.h`, `test.h`; touches `getrusage`; defines `fusage`, `busyloop`, `setup`, `cleanup`, `main`; uses LTP safe helpers such as `SAFE_GETRUSAGE`, `SAFE_STRTOL`.

Control flow centers on `fusage`, `busyloop`, `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `sys/types.h`, `sys/resource.h`, `sys/time.h`, `errno.h`, `stdio.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c -->
