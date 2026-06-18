<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage02.c

Purpose: AUTHOR : Saji Kumar.V.R <saji.kumar@wipro.com> Verify that getrusage() fails with: - EINVAL with invalid who - EFAULT with invalid usage pointer

Important APIs/types/functions: includes `errno.h`, `sched.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`; touches `getrusage`, `raw syscall path`; defines `libc_getrusage`, `sys_getrusage`, `verify_getrusage`, `setup`.

Control flow centers on `libc_getrusage`, `sys_getrusage`, `verify_getrusage`, `setup`. The `struct tst_test` registration wires `.test`, `.setup`, `.tcnt`, `.test_variants` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `errno.h`, `sched.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TCONF`, `TST_EXP_FAIL`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage02.c -->
