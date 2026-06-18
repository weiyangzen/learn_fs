<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl01.c

Purpose: DESCRIPTION: Testcase for testing the basic functionality of sysctl(2) system call. This testcase attempts to read the kernel parameters by using sysctl({CTL_KERN, KERN_* }, ...) and compares it with the known values. get kernel name and information revert uname change in case of kGraft/livepatch

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `string.h`, `linux/version.h`, `sys/utsname.h`, `linux/unistd.h`, `linux/sysctl.h`, `tst_test.h`; exercises `sysctl`, `uname`, `read`, `raw syscall path`; defines `verify_sysctl`, `setup`.

Control flow centers on `verify_sysctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test` into the runner. Named case hints include `KERN_OSTYPE`, `KERN_OSRELEASE`, `KERN_VERSION`.

State and persistence behavior: Runtime state is legacy `_sysctl` kernel name tables and userspace buffers; modern kernels may disable or reject this deprecated interface.

Dependencies and integration points: Depends on `lapi/sysctl.h`, raw `_sysctl` availability, kernel config permitting the legacy syscall, and root privileges for some namespace/table access. Direct include dependencies include `errno.h`, `stdio.h`, `string.h`, `linux/version.h`, `sys/utsname.h`, `linux/unistd.h`.

Risks and test signals: The `_sysctl` syscall is deprecated and often disabled, so TCONF is a normal signal on modern kernels. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl01.c -->
