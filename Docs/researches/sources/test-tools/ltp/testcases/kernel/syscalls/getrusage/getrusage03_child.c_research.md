<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03_child.c

Purpose: Companion executable for getrusage03 that consumes memory, forks grandchildren, and reports ru_maxrss behavior after exec/fork combinations.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`, `getrusage03.h`; touches `fork`; defines `main`; uses LTP safe helpers such as `SAFE_GETRUSAGE`, `SAFE_STRTOL`.

Control flow centers on `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `stdlib.h`, `tst_test.h`, `getrusage03.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_NO_DEFAULT_MAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03_child.c -->
