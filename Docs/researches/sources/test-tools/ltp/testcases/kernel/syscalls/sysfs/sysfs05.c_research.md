<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs05.c

Purpose: This test case checks whether sysfs(2) system call returns appropriate error number for invalid option and for invalid filesystem name and fs index out of bounds.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; exercises `sysfs`, `raw syscall path`; defines `verify_sysfs05`, `setup`; uses constants `EFAULT`, `EINVAL`.

Control flow centers on `verify_sysfs05`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test` into the runner. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs05.c -->
