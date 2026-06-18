<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open01.c

Purpose: Basic pidfd_open() test: - Fetch the PID of the current process and try to get its file descriptor. - Check that the close-on-exec flag is set on the file descriptor.

Important APIs/types/functions: includes `unistd.h`, `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`; defines `run`, `cleanup`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `unistd.h`, `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_FD_SILENT`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open01.c -->
