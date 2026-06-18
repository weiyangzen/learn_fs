<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module02.c

Purpose: Negative `finit_module()` path checking invalid fd, invalid params, malformed module contents, and permission-related errors. Source notes: \ Basic finit_module() failure tests. [Algorithm] Tests various failure scenarios for finit_module(). Insert module twice SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (155 lines, 3813 bytes).

Important APIs/types/functions: calls/wrappers: finit_module(), TST_CAP, SAFE_MKDIR, SAFE_OPEN, SAFE_CLOSE, TST_EXP_FAIL; types/structs: struct tst_cap, struct tcase, struct tst_test, struct tst_tag; functions: bad_fd_setup, dir_setup, setup, cleanup, run; local macros/constants: MODULE_NAME, TEST_DIR.

Control flow: setup path: bad_fd_setup, dir_setup, setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, kernel module load/unload state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `linux/capability.h`, `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`, `tst_capability.h`; integrates with the LTP finit_module syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; kernel config, module signing, and privilege policy affect results; bad-address tests are ABI-sensitive.

Test signals: explicit failure reporting; errno checks: ENOEXEC, EBADF, EISDIR, EINVAL, EFAULT, EPERM, EEXIST, EKEYREJECTED, ETXTBSY; key constants: O_RDONLY, O_CLOEXEC, O_WRONLY, O_RDWR, O_DIRECTORY; harness metadata: .tags, .test, .tcnt, .setup, .cleanup, .needs_tmpdir, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module02.c -->
