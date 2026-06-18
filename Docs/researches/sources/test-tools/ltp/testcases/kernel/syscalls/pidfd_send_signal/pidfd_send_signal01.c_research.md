<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal01.c

Purpose: Tests if the pidfd_send_signal syscall behaves like rt_sigqueueinfo when a pointer to a siginfo_t struct is passed.

Important APIs/types/functions: includes `signal.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`; exercises `pidfd_send_signal`; defines `received_signal`, `verify_pidfd_send_signal`, `setup`, `cleanup`; uses flags/constants `O_CLOEXEC`, `O_DIRECTORY`.

Control flow centers on `received_signal`, `verify_pidfd_send_signal`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is pidfd-backed signal delivery to forked children and permission checks for signal numbers, info pointers, and pidfd validity.

Dependencies and integration points: Depends on pidfd_send_signal syscall wrappers, forked children, signal handlers, and permission/error-path helpers. Direct include dependencies include `signal.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal01.c -->
