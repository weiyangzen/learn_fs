<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll04.c

Purpose: Check that poll() reports POLLNVAL for invalid file descriptors.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `sys/poll.h`, `tst_test.h`; exercises `poll`; defines `verify_pollnval`, `setup`, `cleanup`; uses flags/constants `POLLIN`, `POLLNVAL`.

Control flow centers on `verify_pollnval`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `unistd.h`, `errno.h`, `sys/poll.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_EXPR`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll04.c -->
