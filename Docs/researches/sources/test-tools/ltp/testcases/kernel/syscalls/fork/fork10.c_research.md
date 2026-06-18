<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork10.c

Purpose: Stresses repeated fork/wait cycles and validates no unexpected child failures. Source notes: 07/2001 Ported by Wayne Boyer \ This test verifies inheritance of file descriptors from parent to child process. We open a file from parent, then we check if file offset changes accordingly with file descriptor usage. [Algorithm] Test steps are the following: - create a file made in three parts -> | aa..a | bb..b | cc..c | - from parent, open the file - from child, move file offset after the first part - from parent, read second part and check if it's | bb..b | - from child, read third part and check if it's | cc..c | Test passes if we were able to read the correct file parts from parent and child. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (99 lines, 2113 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_OPEN, SAFE_FORK, SAFE_LSEEK, SAFE_WAIT, SAFE_READ, TST_EXP_EXPR, SAFE_CLOSE, SAFE_CREAT, SAFE_WRITE; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: FILENAME, DATASIZE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: harness metadata: .forks_child, .needs_tmpdir, .test_all, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork10.c -->
