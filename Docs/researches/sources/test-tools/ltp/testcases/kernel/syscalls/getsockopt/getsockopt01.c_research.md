<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that getsockopt() returns the proper errno for various failure cases: - EBADF on a not open file - ENOTSOCK on a file descriptor not linked to a socket - EFAULT on invalid address of value or length - EOPNOTSUPP on invalid option name or protocol - EINVAL on an invalid optlen

Important APIs/types/functions: includes `tst_test.h`; touches `getsockopt`, `socket`; defines `check_getsockopt`, `setup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_OPEN`, `SAFE_SOCKET`.

Control flow centers on `check_getsockopt`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `ENOPROTOOPT`, `ENOTSOCK`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is socket option storage, peer credentials, and connected UNIX/TCP socket endpoints.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `ENOPROTOOPT`, `ENOTSOCK`, `EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt01.c -->
