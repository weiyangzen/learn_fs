<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite02.c

Purpose: Test basic error handling of the pwrite syscall. - ESPIPE when attempted to write to an unnamed pipe - EINVAL the specified offset position was invalid - EBADF fd is not a valid file descriptor - EBADF fd is not open for writing - EFAULT when attempted to write with buf outside accessible address space sighandler - handle SIGXFSZ This is here to start looking at a failure in test case #2. This test case passes on a machine running RedHat 6.2 but it will fail on a machine running RedHat 7.1.

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `string.h`, `tst_test.h`; exercises `pipe`, `pwrite`, `write`; defines `sighandler`, `verify_pwrite`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `sighandler`, `verify_pwrite`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `ESPIPE`.

State and persistence behavior: Runtime state is file content written at explicit offsets, descriptor offsets that should not move for `pwrite()`, and Linux `O_APPEND` behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `unistd.h`, `string.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite02.c -->
