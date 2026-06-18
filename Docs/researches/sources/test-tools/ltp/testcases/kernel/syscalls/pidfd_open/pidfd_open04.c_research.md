<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open04.c

Purpose: Verify that the PIDFD_NONBLOCK flag works with pidfd_open() and that waitid() with a non-blocking pidfd returns EAGAIN.

Important APIs/types/functions: includes `unistd.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`; defines `run`, `setup`, `cleanup`; uses flags/constants `O_NONBLOCK`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path expectations include `EAGAIN`, `EINVAL`.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `unistd.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_EXP_FAIL`, `TST_EXP_FD_SILENT`, `TST_RET`, `TST_RETRY_FUNC`, `TST_RETVAL_EQ0`, `TTERRNO`; checks errno values `EAGAIN`, `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open04.c -->
