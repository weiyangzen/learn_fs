<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl38.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl38.c

Purpose: Dnotify regression test for `fcntl(F_NOTIFY)` and `fcntl(F_SETSIG)`, proving a `DN_ATTRIB` change on a watched subdirectory is reported both to the parent directory watch and the subdirectory watch. Source notes: Started by Amir Goldstein <amir73il@gmail.com> DESCRIPTION Check that dnotify event is reported to both parent and subdir Watch "." and its children for changes Also watch subdir itself for changes Generate DN_ATTRIB event on subdir that should send a signal on both fds SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (96 lines, 2325 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), sigaction(), SAFE_OPEN, SAFE_CHMOD, SAFE_CLOSE, SAFE_MKDIR; types/structs: struct sigaction, struct tst_test; functions: dnotify_handler, setup_dnotify, verify_dnotify, setup, cleanup; local macros/constants: TEST_DIR, TEST_SIG.

Control flow: setup path: setup_dnotify, setup; exercise path: verify_dnotify; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers; declares kernel configuration requirements.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: SIGRTMIN, F_SETSIG, F_NOTIFY, O_RDONLY; harness metadata: .needs_tmpdir, .setup, .cleanup, .test_all, .needs_kconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl38.c -->
