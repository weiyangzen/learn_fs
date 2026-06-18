<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe07.c

Purpose: Ported by Paul Larson Verify that, pipe(2) syscall can open the maximum number of file descriptors permitted.

Important APIs/types/functions: includes `tst_test.h`, `stdlib.h`; exercises `pipe`; defines `record_open_fds`, `setup`, `run`, `cleanup`.

Control flow centers on `record_open_fds`, `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path expectations include `EMFILE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TINFO`, `TST_EXP_EQ_LI`, `TST_RET`; checks errno values `EMFILE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe07.c -->
