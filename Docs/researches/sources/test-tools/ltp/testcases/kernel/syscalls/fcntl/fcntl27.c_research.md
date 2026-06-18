<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl27.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl27.c

Purpose: Modern negative lease test proving `F_SETLEASE/F_RDLCK` fails with `EAGAIN` for selected open-mode combinations. Source notes: Author: Jacky Malcles \ Basic test for fcntl(2) using F_SETLEASE and F_RDLCK argument, testing O_RDWR and O_WRONLY. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (45 lines, 990 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_OPEN, TST_EXP_FAIL, SAFE_CLOSE; types/structs: struct test_case, struct tst_test; functions: verify_fcntl; local macros/constants: TC.

Control flow: exercise path: verify_fcntl; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit failure reporting; errno checks: EAGAIN; key constants: F_SETLEASE, F_RDLCK, O_RDWR, O_WRONLY, O_CREAT; harness metadata: .test, .tcnt, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl27.c -->
