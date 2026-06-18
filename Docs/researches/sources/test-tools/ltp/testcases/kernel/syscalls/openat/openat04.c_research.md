<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat04.c

Purpose: Regression test for `O_TMPFILE` setgid/umask stripping on noacl filesystems, ensuring group execute and setgid bits are filtered correctly.

Important APIs/types/functions: includes `stdlib.h`, `sys/types.h`, `pwd.h`, `sys/mount.h`, `unistd.h`, `stdio.h`, `tst_test.h`, `lapi/fcntl.h`; exercises `openat`, `mount`, `umount`, `fcntl`; defines `do_mount`, `open_tmpfile_supported`, `setup`, `file_test`, `run`, `cleanup`; uses flags/constants `AT_FDCWD`, `AT_SYMLINK_FOLLOW`, `O_DIRECTORY`, `O_RDONLY`, `O_RDWR`, `O_TMPFILE`.

Control flow centers on `do_mount`, `open_tmpfile_supported`, `setup`, `file_test`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root`, `.all_filesystems`, `.mntpoint`, `.skip_filesystems` into the LTP runner. Named case hints include `exfat`, `linux-git`. Error-path expectations include `EINVAL`, `ENOTSUP`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `stdlib.h`, `sys/types.h`, `pwd.h`, `sys/mount.h`, `unistd.h`, `stdio.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_EXP_EQ_LI`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat04.c -->
