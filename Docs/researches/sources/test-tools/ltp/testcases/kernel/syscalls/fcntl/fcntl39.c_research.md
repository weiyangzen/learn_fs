<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl39.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl39.c

Purpose: Dnotify rename regression test for `fcntl(F_NOTIFY)` with `DN_RENAME`, proving rename notifications are delivered only for renames inside the watched parent and not for moves into or out of the watched directory. Source notes: Started by Amir Goldstein <amir73il@gmail.com> \ Check that dnotify DN_RENAME event is reported only on rename inside same parent. Watch renames inside ".", but not in and out of "." Also watch for renames inside subdir, but not in and out of subdir Rename file from "." to subdir should not generate DN_RENAME on either Rename subdir itself should generate DN_RENAME on ".", but not on itself Cleanup before rerun SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (130 lines, 3202 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), sigaction(), SAFE_OPEN, SAFE_RENAME, SAFE_CLOSE, SAFE_MKDIR, SAFE_TOUCH; types/structs: struct sigaction, struct tst_test; functions: dnotify_handler, setup_dnotify, verify_dnotify, setup, cleanup; local macros/constants: TEST_DIR, TEST_DIR2, TEST_FILE, TEST_SIG.

Control flow: setup path: setup_dnotify, setup; exercise path: verify_dnotify; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `fcntl.h`, `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers; declares kernel configuration requirements.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: SIGRTMIN, F_SETSIG, F_NOTIFY, O_RDONLY; harness metadata: .needs_tmpdir, .setup, .cleanup, .test_all, .needs_kconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl39.c -->
