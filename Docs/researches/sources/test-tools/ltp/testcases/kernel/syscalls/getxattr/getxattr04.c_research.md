<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr04.c

Purpose:  This is a regression test for the race between getting an existing xattr and setting/removing a large xattr. This bug leads to that getxattr() fails to get an existing xattr and returns ENOATTR in xfs filesystem. This bug has been fixed in: 5a93790d4e2d ("xfs: remove racy hasattr check from attr ops")

Important APIs/types/functions: includes `config.h`, `errno.h`, `sys/types.h`, `string.h`, `stdlib.h`, `signal.h`, `tst_test.h`; touches `getxattr`; defines `sigproc`, `loop_getxattr`, `verify_getxattr`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_REMOVEXATTR`, `SAFE_SETXATTR`, `SAFE_SIGNAL`, `SAFE_TOUCH`.

Control flow centers on `sigproc`, `loop_getxattr`, `verify_getxattr`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.forks_child`, `.test_all`, `.setup` into the LTP runner. Error-path assertions cover `ENOATTR`, `ENODATA`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `config.h`, `errno.h`, `sys/types.h`, `string.h`, `stdlib.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`. Expected errno values include `ENOATTR`, `ENODATA`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr04.c -->
