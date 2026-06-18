<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open03.c

Purpose: This program opens the PID file descriptor of the child process created with fork(). It then uses poll to monitor the file descriptor for process exit, as indicated by an EPOLLIN event.

Important APIs/types/functions: includes `poll.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`, `poll`, `fork`; defines `run`; uses flags/constants `POLLIN`.

Control flow centers on `run`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.forks_child` into the LTP runner. Error-path expectations include `EPOLLIN`.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `poll.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FD_SILENT`, `TST_RET`; checks errno values `EPOLLIN`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open03.c -->
