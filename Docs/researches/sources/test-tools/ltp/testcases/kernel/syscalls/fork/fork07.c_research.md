<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork07.c

Purpose: Regression coverage for fork limits or repeated fork/wait loops. Source notes: 07/2001 Ported by Wayne Boyer 07/2002 Limited forking and split "infinite forks" testcase to fork12.c by Nate Straz \ Check that all children inherit parent's file descriptor. Parent opens a file and forks children. Each child reads a byte and checks that the value is correct. Parent checks that correct number of bytes was consumed from the file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (70 lines, 1413 bytes).

Important APIs/types/functions: calls/wrappers: read(), SAFE_OPEN, SAFE_FORK, SAFE_READ, SAFE_CLOSE; types/structs: struct tst_test; functions: run, setup, cleanup; local macros/constants: NFORKS, TESTFILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDONLY; harness metadata: .forks_child, .needs_tmpdir, .cleanup, .setup, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork07.c -->
