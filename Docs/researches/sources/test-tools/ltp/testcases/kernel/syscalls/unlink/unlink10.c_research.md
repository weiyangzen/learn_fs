<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink10.c

Purpose: Verify that :manpage:`unlink(2)`: fails with EROFS when target file is on a read-only filesystem.

Important APIs/types/functions: includes `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`; exercises `unlink`, `ioctl`, `read`; defines `run`; uses constants `EROFS`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all`, `.needs_root`, `.mntpoint` into the runner. Error-path expectations include `EROFS`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EROFS`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink10.c -->
