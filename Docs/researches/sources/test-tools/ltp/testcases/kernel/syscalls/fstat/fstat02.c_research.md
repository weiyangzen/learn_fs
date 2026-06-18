<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat02.c

Purpose: Validates `fstat()` metadata fields for an open temporary file. Source notes: 07/2001 Ported by Wayne Boyer 05/2019 Ported to new library: Christian Amann <camann@suse.com> \ Tests if fstat() returns correctly and reports correct file information using the stat structure. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (62 lines, 1357 bytes).

Important APIs/types/functions: calls/wrappers: fstat(), TST_EXP_PASS, TST_EXP_EQ_LU, TST_EXP_EQ_LI, SAFE_OPEN, SAFE_LINK, SAFE_CLOSE; types/structs: struct stat, struct tst_test; functions: run, setup, cleanup; local macros/constants: TESTFILE, LINK_TESTFILE, FILE_SIZE, FILE_MODE, NLINK.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`; integrates with the LTP fstat syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; key constants: O_WRONLY, O_CREAT; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstat/fstat02.c -->
