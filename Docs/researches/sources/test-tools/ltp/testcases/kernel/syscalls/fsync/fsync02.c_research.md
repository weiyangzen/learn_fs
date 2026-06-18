<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync02.c

Purpose: Checks `fsync()` error behavior for invalid descriptors and descriptor states. Source notes: Test Description: Test fsync() return value on test file fsync() has to finish within TIME_LIMIT. free blocks avail to non-superuser SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (119 lines, 2692 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), SAFE_OPEN, SAFE_FCNTL, SAFE_WRITE, SAFE_LSEEK, SAFE_FTRUNCATE, SAFE_CLOSE; types/structs: struct statvfs, struct tst_test; functions: setup, run, cleanup; local macros/constants: BLOCKSIZE, MAXBLKS, BUF_SIZE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `stdlib.h`, `sys/types.h`, `sys/statvfs.h`, `fcntl.h`, `sys/resource.h`, `time.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT, O_TRUNC, F_SETFL, O_LARGEFILE; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir, .timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync02.c -->
