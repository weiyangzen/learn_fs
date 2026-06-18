<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/getpeername01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/getpeername01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getpeername() returns the proper errno for various failure cases: - EBADF on invalid address. - ENOTSOCK on socket opened on /dev/null. - ENOTCONN on socket not connected. - EINVAL on negative addrlen. - EFAULT on invalid addr/addrlen pointers.

Important APIs/types/functions: includes `tst_test.h`; touches `getpeername`, `socket`; defines `setup_fd_file`, `setup_fd_stream`, `cleanup_fd`, `setup_pair`, `cleanup_pair`, `verify_getpeername`, `setup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SOCKET`, `SAFE_SOCKETPAIR`.

Control flow centers on `setup_fd_file`, `setup_fd_stream`, `cleanup_fd`, `setup_pair`, `cleanup_pair`, `verify_getpeername`, `setup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `ENOTCONN`, `ENOTSOCK`.

State and persistence behavior: Runtime state is socket endpoint state, including unconnected sockets and invalid descriptors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `ENOTCONN`, `ENOTSOCK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpeername/getpeername01.c -->
