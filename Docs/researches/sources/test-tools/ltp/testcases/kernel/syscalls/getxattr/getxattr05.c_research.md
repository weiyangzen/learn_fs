<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr05.c

Purpose:  This test verifies that: - Without a user namespace, getxattr(2) should get same data when acquiring the value of system.posix_acl_access twice. - With/Without mapped root UID in a user namespaces, getxattr(2) should get same data when acquiring the value of system.posix_acl_access twice. This issue included by getxattr05 has been fixed in kernel: 82c9a927bc5d ("getxattr: use correct xattr length")

Important APIs/types/functions: includes `config.h`, `errno.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `tst_test.h`, `lapi/sched.h`; touches `getxattr`; defines `verify_getxattr`, `do_unshare`, `do_getxattr`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_ACCESS`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_GETXATTR`, `SAFE_TOUCH`.

Control flow centers on `verify_getxattr`, `do_unshare`, `do_getxattr`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.needs_root`, `.forks_child`, `.setup`, `.cleanup`, `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EOPNOTSUPP`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `config.h`, `errno.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_TEST_TCONF`. Expected errno values include `EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr05.c -->
