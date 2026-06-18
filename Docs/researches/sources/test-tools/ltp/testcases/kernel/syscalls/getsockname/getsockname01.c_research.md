<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/getsockname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/getsockname01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getsockname() returns the proper errno for various failure cases: - EBADF on a not open file - ENOTSOCK on a file descriptor not linked to a socket - EFAULT on invalid socket buffer o invalid socklen - EINVALI on an invalid addrlen

Important APIs/types/functions: includes `tst_test.h`; touches `getsockname`, `socket`; defines `check_getsockname`, `setup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_OPEN`, `SAFE_SOCKET`.

Control flow centers on `check_getsockname`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `EINVALI`, `ENOTSOCK`.

State and persistence behavior: Runtime state is local socket address binding and invalid descriptor/address-length combinations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `EINVALI`, `ENOTSOCK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockname/getsockname01.c -->
