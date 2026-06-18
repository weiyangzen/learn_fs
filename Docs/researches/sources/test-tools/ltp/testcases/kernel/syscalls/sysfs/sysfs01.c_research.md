<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs01.c

Purpose: This test is run for option 1 for sysfs(2). Translate the filesystem identifier string fsname into a filesystem type index. option 1, buf holds fs name

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `sysfs`, `raw syscall path`; defines `verify_sysfs01`.

Control flow centers on `verify_sysfs01`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is the legacy `sysfs(2)` filesystem type registry and indexes/names returned through libc or raw syscall wrappers.

Dependencies and integration points: Depends on libc or raw `sysfs(2)` wrappers and kernel support for the deprecated filesystem type query API. Direct include dependencies include `errno.h`, `unistd.h`, `sys/syscall.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The `sysfs(2)` API is obsolete and filesystem type ordering can vary across kernels. Test signals: reports through `TST_EXP_POSITIVE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysfs/sysfs01.c -->
