<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs01.c

Purpose: Validates successful `fstatfs()` on descriptors and checks returned filesystem statistics are sensible. Source notes: \ Verify that fstatfs() syscall executes successfully for all available filesystems. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (66 lines, 1212 bytes).

Important APIs/types/functions: calls/wrappers: fstatfs(), TST_EXP_PASS, SAFE_OPEN, SAFE_PIPE, SAFE_CLOSE; types/structs: struct tcase, struct statfs, struct tst_test; functions: run, setup, cleanup; local macros/constants: MNT_POINT, TEMP_FILE.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `tst_test.h`; integrates with the LTP fstatfs syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .setup, .cleanup, .tcnt, .test, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatfs/fstatfs01.c -->
