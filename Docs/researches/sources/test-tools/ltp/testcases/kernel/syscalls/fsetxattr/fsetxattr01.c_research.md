<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr01.c

Purpose: Sets extended attributes through file descriptors and verifies create/replace semantics and stored values. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Basic tests for fsetxattr(2) and make sure fsetxattr(2) handles error conditions correctly. There are 9 test cases: 1. Any other flags being set except XATTR_CREATE and XATTR_REPLACE, fsetxattr(2) should return -1 and set errno to EINVAL 2. With XATTR_REPLACE flag set but the attribute does not exist, fsetxattr(2) should return -1 and set errno to ENODATA 3. Create new attr with name length greater than XATTR_NAME_MAX(255) fsetxattr(2) should return -1 and set errno to ERANGE 4. Create new attr whose value length is greater than XATTR_SIZE_MAX(65536) fsetxattr(2) should return -1 and set errno to E2BIG 5. Create new attr whose value length is zero, fsetxattr(2) should succeed 6. Replace the attr value without XATTR_REPLACE flag being set, fsetxattr(2) should return -1 and set errno... The file was read in full for this report (230 lines, 5682 bytes).

Important APIs/types/functions: calls/wrappers: fsetxattr(), SAFE_FSETXATTR, SAFE_FREMOVEXATTR, SAFE_CLOSE, SAFE_MALLOC, SAFE_TOUCH, SAFE_OPEN, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_fsetxattr, cleanup, setup; local macros/constants: XATTR_NAME_MAX, XATTR_NAME_LEN, XATTR_SIZE_MAX, XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, FNAME.

Control flow: setup path: setup; exercise path: verify_fsetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fsetxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, ENODATA, ERANGE, E2BIG, EEXIST, EFAULT, EOPNOTSUPP; key constants: O_RDONLY; harness metadata: .timeout, .setup, .test, .cleanup, .tcnt, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr01.c -->
