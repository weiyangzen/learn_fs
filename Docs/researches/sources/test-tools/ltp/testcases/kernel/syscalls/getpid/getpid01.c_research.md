<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid01.c

Purpose:  Verify that :manpage:`getpid(2)` system call returns process ID in range <2, PID_MAX>.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`; touches `getpid`; defines `setup`, `verify_getpid`; uses LTP safe helpers such as `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_WAIT`.

Control flow centers on `setup`, `verify_getpid`. The `struct tst_test` registration wires `.setup`, `.forks_child`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is process identity across parent/child relationships and kernel PID range limits.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid01.c -->
