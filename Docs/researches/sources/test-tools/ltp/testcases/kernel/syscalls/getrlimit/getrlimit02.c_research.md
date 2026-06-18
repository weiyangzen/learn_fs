<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit02.c

Purpose: AUTHOR: Suresh Babu V. <suresh.babu@wipro.com> Verify that, getrlimit(2) returns -1 and sets errno to - EFAULT if an invalid address is given for address parameter. - EINVAL if an invalid resource type (RLIM_NLIMITS is a out of range resource type) is passed.

Important APIs/types/functions: includes `sys/resource.h`, `tst_test.h`; touches `getrlimit`; defines `verify_getrlimit`.

Control flow centers on `verify_getrlimit`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is per-process resource limit structures and architecture-specific syscall ABI representations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/resource.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit02.c -->
