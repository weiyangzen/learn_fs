<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr02.c

Purpose:  In the user.* namespace, only regular files and directories can have extended attributes. Otherwise getxattr(2) will return -1 and set errno to ENODATA. There are 4 test cases: - Get attribute from a FIFO, setxattr(2) should return -1 and set errno to ENODATA - Get attribute from a char special file, setxattr(2) should return -1 and set errno to ENODATA - Get attribute from a block special file, setxattr(2) should return -1 and set errno to ENODATA - Get attribute from a UNIX domain socket, setxattr(2) should retu

Important APIs/types/functions: includes `sys/types.h`, `sys/sysmacros.h`, `sys/xattr.h`, `stdio.h`, `stdlib.h`, `tst_res_flags.h`, `tst_test.h`, `tst_test_macros.h`; touches `getxattr`, `socket`; defines `run`, `setup`; uses LTP safe helpers such as `SAFE_TOUCH`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.setup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `ENODATA`, `ENOTSUP`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `sys/types.h`, `sys/sysmacros.h`, `sys/xattr.h`, `stdio.h`, `stdlib.h`, `tst_res_flags.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `ENODATA`, `ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr02.c -->
