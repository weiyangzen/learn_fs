<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen02.c

Purpose: Negative `fsopen()` coverage for invalid filesystem names, bad flags, and unsupported kernel behavior. Source notes: Basic fsopen() failure tests. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (58 lines, 1154 bytes).

Important APIs/types/functions: calls/wrappers: fsopen(), SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: setup, run.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsopen syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODEV, EINVAL; harness metadata: .tcnt, .test, .setup, .needs_root, .needs_device.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsopen/fsopen02.c -->
