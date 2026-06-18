<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage01.c

Purpose: AUTHOR: Saji Kumar.V.R <saji.kumar@wipro.com> Test that getrusage() with RUSAGE_SELF and RUSAGE_CHILDREN succeeds.

Important APIs/types/functions: includes `tst_test.h`; touches `getrusage`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage01.c -->
