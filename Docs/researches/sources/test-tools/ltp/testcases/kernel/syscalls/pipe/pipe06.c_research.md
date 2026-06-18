<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe06.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that, pipe(2) syscall fails with errno EMFILE when limit on the number of open file descriptors has been reached.

Important APIs/types/functions: includes `tst_test.h`, `stdlib.h`; exercises `pipe`; defines `setup`, `run`, `cleanup`.

Control flow centers on `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path expectations include `EMFILE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TINFO`, `TST_EXP_FAIL`; checks errno values `EMFILE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe06.c -->
