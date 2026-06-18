<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr05.c

Purpose: Privilege and capability-sensitive file attribute test for flags that require elevated rights or filesystem support. Source notes: \ Verify that `file_setattr` is correctly raising EOPNOTSUPP when filesystem doesn't support FSX operations. EINVAL is raised before EOPNOTSUPP vfat is not implementing file_[set|get]attr SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (63 lines, 1419 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_FAIL, SAFE_TOUCH, SAFE_STAT; types/structs: struct file_attr, struct stat, struct tst_test, struct tst_buffers, struct tst_tag; functions: run, setup; local macros/constants: MNTPOINT, FILEPATH, BLOCKS, PROJID.

Control flow: setup path: setup; exercise path: run.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit failure reporting; errno checks: EOPNOTSUPP, EINVAL; key constants: AT_FDCWD, FS_XFLAG_EXTSIZE, FS_XFLAG_COWEXTSIZE; harness metadata: .test_all, .setup, .needs_root, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr05.c -->
