<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl40.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl40.c

Purpose: Basic `fcntl(F_CREATED_QUERY)` test that distinguishes descriptors opened on an existing file from a descriptor that actually created a file with `O_CREAT | O_CLOEXEC`. Source notes: \ Basic test for fcntl using F_CREATED_QUERY. Verify if the fcntl() syscall is recognizing whether a file has been created or not via O_CREAT when O_CLOEXEC is also used. Test is based on a kernel selftests commit d0fe8920cbe4. We didn't create "/dev/null". We're opening it again, so no positive creation check. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (46 lines, 1099 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_OPEN, TST_EXP_EQ_LI, SAFE_CLOSE, SAFE_UNLINK; types/structs: struct tst_test; functions: verify_fcntl; local macros/constants: TEST_NAME.

Control flow: exercise path: verify_fcntl.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: F_CREATED_QUERY, O_CREAT, O_CLOEXEC, O_RDONLY; harness metadata: .test_all, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl40.c -->
