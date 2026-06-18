<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe10.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that, when a parent process opens a pipe, a child process can read from it.

Important APIs/types/functions: includes `stdio.h`, `tst_test.h`; exercises `pipe`, `read`; defines `run`, `cleanup`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.forks_child`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `stdio.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EQ_LU`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe10.c -->
