<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate01.c

Purpose: Verifies `ftruncate()` shrinks/extends a file, preserves earlier data, zero-fills extension ranges, and updates file size. Source notes: Author: Wayne Boyer \ Verify that, ftruncate() succeeds to truncate a file to a certain length, if the file previously is smaller than the truncated size, ftruncate() shall increase the size of the file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (103 lines, 2133 bytes).

Important APIs/types/functions: calls/wrappers: ftruncate(), SAFE_FSTAT, SAFE_LSEEK, SAFE_READ, SAFE_OPEN, SAFE_CLOSE; types/structs: struct stat, struct tst_test; functions: check_and_report, verify_ftruncate, setup, cleanup; local macros/constants: TESTFILE, TRUNC_LEN1, TRUNC_LEN2, FILE_SIZE.

Control flow: setup path: setup; exercise path: verify_ftruncate; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`, `errno.h`, `string.h`, `tst_test.h`; integrates with the LTP ftruncate syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate01.c -->
