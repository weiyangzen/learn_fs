<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig03.c

Purpose: Additional `fsconfig()` regression coverage for binary parameters, final creation/reconfiguration, or unsupported combinations. Source notes: \ Test for CVE-2022-0185. References links: - https://www.openwall.com/lists/oss-security/2022/01/25/14 - https://github.com/Crusaders-of-Rust/CVE-2022-0185 use same logic in kernel legacy_parse_param function Legacy fsconfig() just copies arguments to buffer SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (98 lines, 2144 bytes).

Important APIs/types/functions: calls/wrappers: fsconfig(), fsopen(), SAFE_CLOSE; types/structs: struct tst_test, struct tst_tag; functions: setup, run, cleanup; local macros/constants: MNTPOINT.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fsmount.h`; integrates with the LTP fsconfig syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; new mount API availability and filesystem support differ by kernel.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL; harness metadata: .timeout, .test_all, .setup, .cleanup, .needs_root, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsconfig/fsconfig03.c -->
