<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr03.c

Purpose:  An empty buffer of size zero can be passed into getxattr(2) to return the current size of the named extended attribute.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `sys/xattr.h`, `tst_safe_macros.h`; touches `getxattr`; defines `run`, `setup`; uses LTP safe helpers such as `SAFE_SETXATTR`, `SAFE_TOUCH`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is filesystem extended attributes, ACL xattrs, namespace mappings, mount capabilities, and racing xattr updates.

Dependencies and integration points: Depends on filesystem xattr support, user/trusted/system xattr namespaces, optional ACL libraries, mounts, and user namespace settings. Direct include dependencies include `config.h`, `tst_test.h`, `sys/xattr.h`, `tst_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_VAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getxattr/getxattr03.c -->
