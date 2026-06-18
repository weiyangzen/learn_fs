<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe08.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that, on any attempt to write to a pipe which is closed for reading will generate a SIGPIPE signal and write will fail with EPIPE errno.

Important APIs/types/functions: includes `tst_test.h`; exercises `pipe`, `write`; defines `sighandler`, `run`, `setup`, `cleanup`.

Control flow centers on `sighandler`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the LTP runner. Error-path expectations include `EPIPE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EQ_LI`, `TST_EXP_FAIL2_SILENT`; checks errno values `EPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe08.c -->
