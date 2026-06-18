<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl03.c

Purpose: DESCRIPTION 1) Call sysctl(2) as a root user, and attempt to write data to the kernel_table[]. Since the table does not have write permissions even for the root, it should fail EPERM. 2) Call sysctl(2) as a non-root user, and attempt to write data to the kernel_table[]. Since the table does not have write permission for the regular user, it should fail with EPERM. NOTE: There is a documentation bug in 2.6.33-rc1 where unfortunately the behavior of sysctl(2) isn't properly documented, as discussed in detail in the following thread: http://sourceforge.net/mailarchive/message.php?msg_name=4B7BA24F.2010705%40linux.vnet.ibm.com. The documentation bug is filed as: https://bugzilla.kernel.org/show_bug.cgi?id=15446 . If you want the message removed, please ask your fellow kernel maintainer to fix their documentation. Thanks! -Ngie

Important APIs/types/functions: includes `sys/types.h`, `sys/wait.h`, `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`, `linux/sysctl.h`, `pwd.h`; exercises `sysctl`, `read`, `write`, `raw syscall path`; defines `verify_sysctl`, `setup`, `do_test`; uses constants `EACCES`, `EPERM`.

Control flow centers on `verify_sysctl`, `setup`, `do_test`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.test_all` into the runner. Error-path expectations include `EACCES`, `EPERM`.

State and persistence behavior: Runtime state is legacy `_sysctl` kernel name tables and userspace buffers; modern kernels may disable or reject this deprecated interface.

Dependencies and integration points: Depends on `lapi/sysctl.h`, raw `_sysctl` availability, kernel config permitting the legacy syscall, and root privileges for some namespace/table access. Direct include dependencies include `sys/types.h`, `sys/wait.h`, `stdio.h`, `errno.h`, `unistd.h`, `linux/unistd.h`.

Risks and test signals: The `_sysctl` syscall is deprecated and often disabled, so TCONF is a normal signal on modern kernels. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EACCES`, `EPERM`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysctl/sysctl03.c -->
