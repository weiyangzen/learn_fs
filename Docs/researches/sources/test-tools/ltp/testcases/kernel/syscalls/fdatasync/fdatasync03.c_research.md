<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync03.c

Purpose: Checks `fdatasync()` on a write-only file descriptor and reports success or expected kernel/libc failure details. Source notes: Author: Sumit Garg <sumit.garg@linaro.org> fdatasync03 It basically tests fdatasync() to sync test file data having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (66 lines, 1393 bytes).

Important APIs/types/functions: calls/wrappers: fdatasync(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_fdatasync; local macros/constants: MNTPOINT, FNAME, FILE_SIZE_MB, FILE_SIZE, MODE.

Control flow: exercise path: verify_fdatasync.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`; integrates with the LTP fdatasync syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, O_CREAT; harness metadata: .timeout, .needs_root, .test_all.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync03.c -->
