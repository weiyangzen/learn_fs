<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl04.c

Purpose: DESCRIPTION 1) Call sysctl(2) with nlen set to 0, and expect ENOTDIR. 2) Call sysctl(2) with nlen greater than CTL_MAXNAME, and expect ENOTDIR. 3) Call sysctl(2) with the address of oldname outside the address space of the process, and expect EFAULT. 4) Call sysctl(2) with the address of soldval outside the address space of the process, and expect EFAULT.

Important APIs/types/functions: includes `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`, `linux/sysctl.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `sysctl`, `raw syscall path`; defines `verify_sysctl`; uses constants `EFAULT`, `ENOTDIR`.

Control flow centers on `verify_sysctl`. The `struct tst_test` registration wires `.tcnt`, `.test` into the runner. Error-path expectations include `EFAULT`, `ENOTDIR`.

State and persistence behavior: Runtime state is legacy `_sysctl` kernel name tables and userspace buffers; modern kernels may disable or reject this deprecated interface.

Dependencies and integration points: Depends on `lapi/sysctl.h`, raw `_sysctl` availability, kernel config permitting the legacy syscall, and root privileges for some namespace/table access. Direct include dependencies include `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`, `linux/sysctl.h`, `tst_test.h`.

Risks and test signals: The `_sysctl` syscall is deprecated and often disabled, so TCONF is a normal signal on modern kernels. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl04.c -->
