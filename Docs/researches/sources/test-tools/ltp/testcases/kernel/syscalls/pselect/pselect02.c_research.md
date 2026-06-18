<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect02.c

Purpose: Verify that pselect() fails with: - EBADF if a file descriptor that was already closed - EINVAL if nfds was negative - EINVAL if the value contained within timeout was invalid

Important APIs/types/functions: includes `tst_test.h`; exercises `pselect`; defines `setup`, `pselect_verify`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `setup`, `pselect_verify`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EINVAL`.

State and persistence behavior: Runtime state is `fd_set` readiness, signal masks, pselect timeout values, and child processes used to deliver signals or produce I/O.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EBADF`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect02.c -->
