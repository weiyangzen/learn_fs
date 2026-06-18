<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt02.c

Purpose:  Test getsockopt(2) for retrieving peer credentials (SO_PEERCRED).

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `tst_test.h`; touches `getpid`, `getsockopt`, `socket`, `accept`; defines `setup`, `fork_func`, `test_function`, `cleanup`; uses LTP safe helpers such as `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_FORK`, `SAFE_LISTEN`, `SAFE_SOCKET`.

Control flow centers on `setup`, `fork_func`, `test_function`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is socket option storage, peer credentials, and connected UNIX/TCP socket endpoints.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getsockopt/getsockopt02.c -->
