<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr01.c

Purpose: Sets an extended attribute and verifies `fgetxattr()` returns the expected value through an open descriptor. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Basic tests for fgetxattr(2) and make sure fgetxattr(2) handles error conditions correctly. There are 3 test cases: 1. Get an non-existing attribute: - fgetxattr(2) should return -1 and set errno to ENODATA 2. Buffer size is smaller than attribute value size: - fgetxattr(2) should return -1 and set errno to ERANGE 3. Get attribute, fgetxattr(2) should succeed: - verify the attribute got by fgetxattr(2) is same as the value we set case 00, get non-existing attribute case 01, small value buffer case 02, get existing attribute SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (150 lines, 3380 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), SAFE_TOUCH, SAFE_OPEN, SAFE_MALLOC, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_fgetxattr, setup, cleanup; local macros/constants: XATTR_SIZE_MAX, XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, XATTR_TEST_INVALID_KEY, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fgetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fgetxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODATA, ERANGE, EOPNOTSUPP; key constants: O_RDONLY; harness metadata: .timeout, .setup, .test, .cleanup, .tcnt, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr01.c -->
