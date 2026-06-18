<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr02.c

Purpose: Negative `fremovexattr()` coverage for invalid descriptors, missing xattrs, and bad names. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Test Name: fremovexattr02 Test cases:: 1) fremovexattr(2) fails if the named attribute does not exist. 2) fremovexattr(2) fails if file descriptor is not valid. 3) fremovexattr(2) fails if named attribute has an invalid address. Expected Results: fremovexattr(2) should return -1 and set errno to ENODATA. fremovexattr(2) should return -1 and set errno to EBADF. fremovexattr(2) should return -1 and set errno to EFAULT. case 1: attribute does not exist case 2: file descriptor is invalid case 3: bad name attribute HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (121 lines, 2487 bytes).

Important APIs/types/functions: calls/wrappers: fremovexattr(), SAFE_CLOSE, SAFE_OPEN, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_fremovexattr, cleanup, setup; local macros/constants: XATTR_TEST_KEY, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fremovexattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `errno.h`, `fcntl.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fremovexattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODATA, EBADF, EFAULT, EOPNOTSUPP; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .setup, .test, .cleanup, .tcnt, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fremovexattr/fremovexattr02.c -->
