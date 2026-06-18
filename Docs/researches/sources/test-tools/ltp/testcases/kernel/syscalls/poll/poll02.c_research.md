<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll02.c

Purpose: Check that :manpage:`poll(2)` timeouts correctly.

Important APIs/types/functions: includes `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_timer_test.h`; exercises `poll`, `fcntl`; defines `sample_fn`, `setup`, `cleanup`; uses flags/constants `POLLIN`.

Control flow centers on `sample_fn`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_timer_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll02.c -->
