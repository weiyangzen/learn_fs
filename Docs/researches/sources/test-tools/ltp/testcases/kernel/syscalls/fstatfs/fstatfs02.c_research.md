<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs02.c

Purpose: Checks `fstatfs()` error behavior for invalid descriptors. Source notes: \ Testcase to check if fstatfs() sets errno correctly. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (74 lines, 1362 bytes).

Important APIs/types/functions: calls/wrappers: fstatfs(), SAFE_FORK, TST_EXP_FAIL, SAFE_WAITPID, SAFE_OPEN, SAFE_CLOSE; types/structs: struct statfs, struct test_case_t, struct tst_test; functions: fstatfs_verify, setup, cleanup.

Control flow: setup path: setup; exercise path: fstatfs_verify; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `sys/types.h`, `sys/statfs.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_macros.h`; integrates with the LTP fstatfs syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose; bad-address tests are ABI-sensitive.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EFAULT; key constants: SIGSEGV, O_RDWR, O_CREAT; harness metadata: .test, .tcnt, .setup, .cleanup, .needs_tmpdir, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs02.c -->
