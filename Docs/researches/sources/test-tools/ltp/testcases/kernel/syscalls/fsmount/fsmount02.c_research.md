<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount02.c

Purpose: Negative `fsmount()` coverage for bad descriptors, bad flags, invalid mount attributes, and errno contracts. Source notes: Basic fsmount() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (81 lines, 1857 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsmount(), fsopen(), SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: cleanup, setup, run; local macros/constants: MNTPOINT.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsmount syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EINVAL; harness metadata: .timeout, .tcnt, .test, .setup, .cleanup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount02.c -->
