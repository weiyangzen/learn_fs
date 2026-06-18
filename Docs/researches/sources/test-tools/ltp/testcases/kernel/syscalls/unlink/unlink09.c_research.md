<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink09.c

Purpose: Verify that :manpage:`unlink(2)`: fails with EPERM when target file is marked as immutable or append-only. inode attributes in tmpfs are supported from kernel 6.0 https://lore.kernel.org/all/20220715015912.2560575-1-tytso@mit.edu/ If unlink() succeeded unexpectedly, test file should be restored.

Important APIs/types/functions: includes `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`; exercises `unlink`, `ioctl`; defines `setup_inode_flag`, `setup`, `cleanup`, `verify_unlink`; uses constants `ENOTTY`, `EPERM`, `FS_APPEND_FL`, `FS_IMMUTABLE_FL`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`.

Control flow centers on `setup_inode_flag`, `setup`, `cleanup`, `verify_unlink`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.cleanup`, `.test`, `.mntpoint`, `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems` into the runner. Named case hints include `fuse`. Error-path expectations include `ENOTTY`, `EPERM`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TST_ERR`, `TST_EXP_FAIL`, `TST_RET`; checks errno values `ENOTTY`, `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink09.c -->
