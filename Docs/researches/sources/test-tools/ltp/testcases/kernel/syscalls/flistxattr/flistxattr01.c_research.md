<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr01.c

Purpose: Sets xattrs and verifies `flistxattr()` returns the expected attribute name list through a descriptor. Source notes: Author: Dejan Jovicevic <dejan.jovicevic@rt-rk.com> Test Name: verify_flistxattr01 Description: The testcase checks the basic functionality of the flistxattr(2). flistxattr(2) retrieves the list of extended attribute names associated with the file itself in the filesystem. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (90 lines, 1768 bytes).

Important APIs/types/functions: calls/wrappers: flistxattr(), SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct tst_test; functions: has_attribute, verify_flistxattr, setup, cleanup; local macros/constants: SECURITY_KEY1, VALUE, VALUE_SIZE, KEY_SIZE.

Control flow: setup path: setup; exercise path: verify_flistxattr; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `sys/types.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP flistxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .needs_root, .test_all, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr01.c -->
