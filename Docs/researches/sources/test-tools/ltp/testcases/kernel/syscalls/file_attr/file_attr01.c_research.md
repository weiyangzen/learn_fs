<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr01.c

Purpose: Validates getting and setting Linux file attribute flags on a regular file. Source notes: \ Verify that `file_getattr` and `file_setattr` syscalls are raising the correct errors according to the invalid input arguments. In particular: - EBADFD: Invalid file descriptor. - ENOENT: File doesn't exist - EFAULT: File name is NULL - EFAULT: File attributes is NULL - EINVAL: File attributes size is zero - E2BIG: File attributes size is too big - EINVAL: Invalid AT flags SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (189 lines, 4167 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_FAIL, SAFE_OPEN, SAFE_CHDIR, SAFE_TOUCH, SAFE_SYSCONF, SAFE_CLOSE; types/structs: struct file_attr, struct tcase, struct tst_test, struct tst_buffers; functions: run, setup, cleanup; local macros/constants: MNTPOINT, FILENAME, NO_FILENAME.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `string.h`, `tst_test.h`, `tst_kconfig.h`, `lapi/fs.h`, `lapi/fcntl.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; bad-address tests are ABI-sensitive.

Test signals: explicit failure reporting; errno checks: EBADFD, ENOENT, EFAULT, EINVAL, E2BIG, EBADF, EOPNOTSUPP; key constants: O_RDONLY; harness metadata: .test, .setup, .cleanup, .tcnt, .needs_root, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr01.c -->
