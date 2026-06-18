<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer02.c

Purpose: 03/2001 - Written by Wayne Boyer Check that getitimer() call fails: 1. EFAULT with invalid itimerval pointer 2. EINVAL when called with an invalid first argument

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `sys/time.h`, `tst_test.h`, `lapi/syscalls.h`; touches `getitimer`, `raw syscall path`; defines `sys_getitimer`, `setup`, `verify_getitimer`, `cleanup`; uses LTP safe helpers such as `SAFE_MALLOC`.

Control flow centers on `sys_getitimer`, `setup`, `verify_getitimer`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is per-process interval timer configuration and the itimerval values returned by getitimer.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `errno.h`, `sys/time.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getitimer/getitimer02.c -->
