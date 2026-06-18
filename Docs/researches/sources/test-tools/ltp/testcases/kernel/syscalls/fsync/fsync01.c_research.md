<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync01.c

Purpose: Basic `fsync()` success test on a writable temporary file. Source notes: AUTHOR : William Roske CO-PILOT : Dave Fenner SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (55 lines, 994 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), SAFE_WRITE, SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fsync, setup, cleanup; local macros/constants: BUF.

Control flow: setup path: setup; exercise path: verify_fsync; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `errno.h`, `stdio.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .cleanup, .setup, .test_all, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync01.c -->
