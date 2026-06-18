<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr01.c

Purpose:  Basic tests for getxattr(2) and make sure getxattr(2) handles error conditions correctly. 1. Get an non-existing attribute, getxattr(2) should return -1 and set errno to ENODATA. 2. Buffer size is smaller than attribute value size, getxattr(2) should return -1 and set errno to ERANGE. 3. Get attribute, getxattr(2) should succeed, and the attribute got by getxattr(2) should be same as the value we set.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`, `sys/xattr.h`; touches `getxattr`; defines `run`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_MALLOC`, `SAFE_SETXATTR`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.needs_root`, `.setup`, `.cleanup`, `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `ENODATA`, `ERANGE`.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `stdlib.h`, `tst_test.h`, `sys/xattr.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_FAIL`, `TST_EXP_VAL`. Expected errno values include `ENODATA`, `ERANGE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr01.c -->
