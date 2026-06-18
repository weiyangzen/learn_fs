<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat03.c

Purpose: Checks `fstat()` error handling for invalid descriptors and descriptor types. Source notes: 07/2001 Ported by Wayne Boyer 05/2019 Ported to new library: Christian Amann <camann@suse.com> Tests different error scenarios: 1) Calls fstat() with closed file descriptor -> EBADF 2) Calls fstat() with an invalid address for stat structure -> EFAULT (or receive signal SIGSEGV) SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (102 lines, 2079 bytes).

Important APIs/types/functions: calls/wrappers: fstat(), SAFE_FORK, SAFE_WAITPID, SAFE_OPEN, SAFE_CLOSE; types/structs: struct stat, struct tcase, struct tst_test; functions: check_fstat, run, setup, cleanup; local macros/constants: TESTFILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `unistd.h`, `wait.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`, `tst_safe_macros.h`; integrates with the LTP fstat syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EFAULT; key constants: SIGSEGV, O_RDWR, O_CREAT; harness metadata: .test, .tcnt, .setup, .cleanup, .needs_tmpdir, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat03.c -->
