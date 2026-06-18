<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr02.c

Purpose: Negative `flistxattr()` coverage for invalid descriptors and bad/undersized buffers. Source notes: Author: Dejan Jovicevic <dejan.jovicevic@rt-rk.com> Test Name: flistxattr02 Description: 1) flistxattr(2) fails if the size of the list buffer is too small to hold the result. 2) flistxattr(2) fails if fd is an invalid file descriptor. Expected Result: 1) flistxattr(2) should return -1 and set errno to ERANGE. 2) flistxattr(2) should return -1 and set errno to EBADF. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (95 lines, 1899 bytes).

Important APIs/types/functions: calls/wrappers: flistxattr(), SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct tst_test; functions: verify_flistxattr, setup, cleanup; local macros/constants: SECURITY_KEY, VALUE, VALUE_SIZE.

Control flow: setup path: setup; exercise path: verify_flistxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `errno.h`, `sys/types.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP flistxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ERANGE, EBADF; key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .needs_root, .test, .tcnt, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flistxattr/flistxattr02.c -->
