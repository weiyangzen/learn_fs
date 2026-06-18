<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid02.c

Purpose:  Check that: - :manpage:`fork(2)` in parent returns the same pid as :manpage:`getpid(2)` in child - :manpage:`getppid(2)` in child returns the same pid as :manpage:`getpid(2)` in parent

Important APIs/types/functions: includes `tst_test.h`; touches `getpid`, `getppid`, `fork`; defines `verify_getpid`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MUNMAP`.

Control flow centers on `verify_getpid`, `setup`, `cleanup`. The `struct tst_test` registration wires `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is process identity across parent/child relationships and kernel PID range limits.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpid/getpid02.c -->
