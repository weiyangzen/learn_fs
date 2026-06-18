<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink05.c

Purpose: Test the basic functionality of :manpage:`unlink(2)`: - :manpage:`unlink(2)` can delete regular file successfully - :manpage:`unlink(2)` can delete fifo file successfully

Important APIs/types/functions: includes `errno.h`, `sys/types.h`, `unistd.h`, `stdio.h`, `tst_test.h`; exercises `unlink`; defines `file_create`, `fifo_create`, `verify_unlink`.

Control flow centers on `file_create`, `fifo_create`, `verify_unlink`. The `struct tst_test` registration wires `.needs_tmpdir`, `.tcnt`, `.test` into the runner.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `errno.h`, `sys/types.h`, `unistd.h`, `stdio.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink05.c -->
