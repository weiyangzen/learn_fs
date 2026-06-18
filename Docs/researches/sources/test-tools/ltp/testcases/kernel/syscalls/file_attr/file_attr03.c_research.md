<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr03.c

Purpose: Tests immutable/append-only style file flags and their effects on write/unlink/truncate behavior. Source notes: \ Verify that `file_setattr` is correctly setting filesystems additional attributes. We are running test on XFS only, since it's the only filesystem currently implementing the features we need. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (76 lines, 1770 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_CREAT, TST_EXP_PASS, SAFE_IOCTL, SAFE_CLOSE, TST_EXP_EQ_LI, SAFE_UNLINK; types/structs: struct fsxattr, struct file_attr, struct tst_test, struct tst_fs, struct tst_buffers; functions: run, setup, cleanup; local macros/constants: MNTPOINT, FILEPATH, BLOCKS, PROJID.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; key constants: AT_FDCWD, FS_IOC_FSGETXATTR, FS_XFLAG_EXTSIZE, FS_XFLAG_COWEXTSIZE; harness metadata: .test_all, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr03.c -->
