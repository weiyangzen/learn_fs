<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount01.c

Purpose: Uses `fsopen`, `fsconfig`, and `fsmount` to build a detached mount and validate successful new mount API behavior. Source notes: Author: Zorro Lang <zlang@redhat.com> Basic fsmount() test. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (127 lines, 3346 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsmount(), fsopen(), SAFE_CLOSE, TST_EXP_VAL, SAFE_UMOUNT; types/structs: struct tcase, struct tst_test; functions: run; local macros/constants: MNTPOINT, TCASE_ENTRY.

Control flow: exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`, `tst_safe_stdio.h`; integrates with the LTP fsmount syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; key constants: AT_FDCWD; harness metadata: .timeout, .tcnt, .test, .setup, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsmount/fsmount01.c -->
