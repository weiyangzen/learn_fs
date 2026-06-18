<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll01.c

Purpose: Ported to LTP: Wayne Boyer Check that :manpage:`poll(2)` works for POLLOUT and POLLIN and that revents is set correctly.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_test.h`; exercises `poll`, `fcntl`; defines `verify_pollout`, `verify_pollin`, `verify_poll`, `setup`, `cleanup`; uses flags/constants `POLLIN`, `POLLOUT`.

Control flow centers on `verify_pollout`, `verify_pollin`, `verify_poll`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `unistd.h`, `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EXPR`, `TST_EXP_VAL`, `TST_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll01.c -->
