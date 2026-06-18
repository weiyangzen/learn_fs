<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal02.c

Purpose: Tests basic error handling of the pidfd_send_signal system call. - EINVAL Pass invalid flag value to syscall (value chosen to be unlikely to collide with future extensions) - EBADF Pass a file descriptor that is corresponding to a regular file instead of a pid directory - EINVAL Pass a signal that is different from the one used to initialize the siginfo_t struct - EPERM Try to send signal to other process (init) with missing privileges

Important APIs/types/functions: includes `pwd.h`, `signal.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`; exercises `pidfd_send_signal`; defines `verify_pidfd_send_signal`, `setup`, `cleanup`; uses flags/constants `O_CLOEXEC`, `O_CREAT`, `O_DIRECTORY`, `O_RDWR`.

Control flow centers on `verify_pidfd_send_signal`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is pidfd-backed signal delivery to forked children and permission checks for signal numbers, info pointers, and pidfd validity.

Dependencies and integration points: Depends on pidfd_send_signal syscall wrappers, forked children, signal handlers, and permission/error-path helpers. Direct include dependencies include `pwd.h`, `signal.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TTERRNO`; checks errno values `EBADF`, `EINVAL`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal02.c -->
