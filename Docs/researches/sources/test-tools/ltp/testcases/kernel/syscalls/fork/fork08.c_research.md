<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork08.c

Purpose: Validates descriptor or file-offset inheritance semantics after fork. Source notes: 07/2001 Ported by Wayne Boyer \ Check that the parent's file descriptors will not be affected by being closed in the child. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (68 lines, 1185 bytes).

Important APIs/types/functions: calls/wrappers: read(), SAFE_OPEN, SAFE_FORK, SAFE_CLOSE, SAFE_READ; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: TESTFILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDONLY; harness metadata: .forks_child, .needs_tmpdir, .cleanup, .setup, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork08.c -->
