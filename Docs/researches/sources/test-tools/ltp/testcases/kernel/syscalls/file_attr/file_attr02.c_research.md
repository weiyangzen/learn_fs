<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr02.c

Purpose: Checks file attribute ioctl error handling for invalid descriptors and unsuitable file types. Source notes: \ Verify that `file_getattr` is correctly reading filesystems additional attributes. We are running test on XFS only, since it's the only filesystem currently implementing the features we need. this will force at least one extent to be allocated SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (109 lines, 2478 bytes).

Important APIs/types/functions: calls/wrappers: mount(), TST_EXP_PASS, TST_EXP_EQ_LI, SAFE_MKDIR, SAFE_STAT, SAFE_OPEN, SAFE_CREAT, SAFE_IOCTL, SAFE_WRITE, SAFE_CLOSE, SAFE_UMOUNT; types/structs: struct fsxattr, struct file_attr, struct stat, struct tst_test, struct tst_fs, struct tst_buffers; functions: run, setup, cleanup; local macros/constants: MNTPOINT, FILENAME, BLOCKS, PROJID.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/mount.h`, `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; errno checks: EOPNOTSUPP; key constants: O_RDONLY, FS_IOC_FSGETXATTR, FS_XFLAG_EXTSIZE, FS_XFLAG_COWEXTSIZE, FS_IOC_FSSETXATTR; harness metadata: .test_all, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr02.c -->
