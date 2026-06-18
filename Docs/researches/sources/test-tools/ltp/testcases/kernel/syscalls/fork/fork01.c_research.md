<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork01.c

Purpose: Basic fork test confirming parent receives child pid, child exits through the expected path, and wait observes the child. Source notes: Author: Kathy Olmsted Co-Pilot: Steve Shaw \ This test verifies that fork returns without error and that it returns the pid of the child. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (75 lines, 1491 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_FORK, SAFE_FILE_PRINTF, SAFE_WAITPID, SAFE_FILE_SCANF, TST_EXP_EQ_LI, SAFE_CREAT, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fork, setup, cleanup; local macros/constants: KIDEXIT, FILENAME.

Control flow: setup path: setup; exercise path: verify_fork; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, kernel tunables that setup/cleanup must restore, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `string.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; harness metadata: .setup, .cleanup, .needs_tmpdir, .forks_child, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork01.c -->
