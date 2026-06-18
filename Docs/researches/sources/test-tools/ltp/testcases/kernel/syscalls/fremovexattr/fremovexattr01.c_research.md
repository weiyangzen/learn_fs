<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr01.c

Purpose: Sets and removes an xattr through `fremovexattr()`, then verifies it is gone. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Test Name: fremovexattr01 Description: Like removexattr(2), fremovexattr(2) also removes an extended attribute, identified by a name, from a file but, instead of using a filename path, it uses a descriptor. This test verifies that a simple call to fremovexattr(2) removes, indeed, a previously set attribute key/value from a file. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (98 lines, 2186 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), fremovexattr(), removexattr(), SAFE_FSETXATTR, SAFE_CLOSE, SAFE_OPEN, TST_TEST_TCONF; types/structs: struct tst_test; functions: verify_fremovexattr, cleanup, setup; local macros/constants: ENOATTR, XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fremovexattr; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `stdlib.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fremovexattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENOATTR, ENODATA, EOPNOTSUPP; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .setup, .test_all, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr01.c -->
