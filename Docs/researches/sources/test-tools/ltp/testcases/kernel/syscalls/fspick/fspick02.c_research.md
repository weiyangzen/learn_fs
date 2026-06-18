<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick02.c

Purpose: Negative `fspick()` coverage for invalid dirfd/path/flags and inaccessible mount targets. Source notes: Basic fspick() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (55 lines, 1334 bytes).

Important APIs/types/functions: calls/wrappers: fspick(), SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: run; local macros/constants: MNTPOINT.

Control flow: exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fspick syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, ENOENT, EINVAL; key constants: AT_FDCWD; harness metadata: .timeout, .tcnt, .test, .setup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fspick/fspick02.c -->
