<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate03.c

Purpose: Negative `ftruncate()` coverage for socket descriptors, read-only descriptors, bad descriptors, and invalid lengths. Source notes: Author: Jay Huie, Robbie Williamson \ Verify that ftruncate(2) system call returns appropriate error number: 1. EINVAL -- the file is a socket 2. EINVAL -- the file descriptor was opened with O_RDONLY 3. EINVAL -- the length is negative 4. EBADF -- the file descriptor is invalid SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (91 lines, 1892 bytes).

Important APIs/types/functions: calls/wrappers: ftruncate(), SAFE_SOCKET, SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_ftruncate, setup, cleanup; local macros/constants: TESTFILE1, TESTFILE2.

Control flow: setup path: setup; exercise path: verify_ftruncate; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `sys/socket.h`, `tst_test.h`; integrates with the LTP ftruncate syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EBADF; key constants: O_RDONLY, O_CREAT, O_RDWR; harness metadata: .tcnt, .test, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate03.c -->
