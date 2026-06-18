<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/fpathconf01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/fpathconf01.c

Purpose: Calls `fpathconf()` for supported `_PC_*` names on an open descriptor and checks returned values/errors. Source notes: \ Check the basic functionality of the fpathconf(2) system call. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (54 lines, 1095 bytes).

Important APIs/types/functions: calls/wrappers: fpathconf(), TST_EXP_POSITIVE, SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_fpathconf, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_fpathconf; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`; integrates with the LTP fpathconf syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: O_RDWR, O_CREAT; harness metadata: .needs_tmpdir, .test, .tcnt, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fpathconf/fpathconf01.c -->
