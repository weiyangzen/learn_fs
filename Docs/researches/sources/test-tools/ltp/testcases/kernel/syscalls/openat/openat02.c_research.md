<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02.c

Purpose: This test case will verify following scenarios of :manpage:`openat(2)`. - openat() succeeds to open a file in append mode, when 'flags' is set to O_APPEND. - openat() succeeds to enable the close-on-exec flag for a file descriptor, when 'flags' is set to O_CLOEXEC. - openat() succeeds to allow files whose sizes cannot be represented in an off_t but can be represented in an off_t to be opened, when 'flags' is set to O_LARGEFILE. - openat() succeeds to not update the file last access time (st_atime in the inode) when the file is read, when 'flags' is set to O_NOATIME. - openat() succeeds to open the file failed if

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`, `lapi/mount.h`, `tst_test.h`; exercises `openat`, `fork`, `execlp`, `mount`, `read`, `lseek`; defines `testfunc_append`, `testfunc_cloexec`, `testfunc_largefile`, `testfunc_noatime`, `testfunc_nofollow`, `testfunc_trunc`, `verify_openat`, `setup`, `cleanup`; uses flags/constants `AT_FDCWD`, `O_APPEND`, `O_CLOEXEC`, `O_CREAT`, `O_LARGEFILE`, `O_NOATIME`, `O_NOFOLLOW`, `O_RDONLY`, `O_RDWR`, `O_TRUNC`.

Control flow centers on `testfunc_append`, `testfunc_cloexec`, `testfunc_largefile`, `testfunc_noatime`, `testfunc_nofollow`, `testfunc_trunc`, `verify_openat`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt`, `.forks_child`, `.all_filesystems`, `.needs_root`, `.mount_device`, `.mntpoint`, `.filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `noatime`, `vfat`. Error-path expectations include `ELOOP`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_EXP_FD`, `TST_EXP_FD_OR_FAIL`, `TST_RET`, `TTERRNO`; checks errno values `ELOOP`; uses child exit/wait status as part of the signal; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02.c -->
