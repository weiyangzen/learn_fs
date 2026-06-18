<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe03.c

Purpose: Verify that, an attempt to write to the read end of a pipe fails with EBADF and an attempt to read from the write end of a pipe also fails with EBADF.

Important APIs/types/functions: includes `tst_test.h`; exercises `pipe`, `read`, `write`; defines `verify_pipe`, `cleanup`.

Control flow centers on `verify_pipe`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup` into the LTP runner. Error-path expectations include `EBADF`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EBADF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe03.c -->
