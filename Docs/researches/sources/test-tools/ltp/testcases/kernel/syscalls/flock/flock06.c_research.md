<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock06.c

Purpose: Regression test for flock behavior across fork/exec or duplicated descriptor style scenarios. Source notes: Author: Matthew Wilcox \ Test verifies that flock locks held on one file descriptor conflict with flock locks held on a different file descriptor. The process opens two file descriptors on the same file. It acquires an exclusive flock on the first descriptor, checks that attempting to acquire an flock on the second descriptor fails. Then it removes the first descriptor's lock and attempts to acquire an exclusive lock on the second descriptor. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (69 lines, 1775 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tst_test; functions: verify_flock, setup.

Control flow: setup path: setup; exercise path: verify_flock.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, LOCK_EX, LOCK_NB, LOCK_UN, O_CREAT, O_TRUNC; harness metadata: .test_all, .needs_tmpdir, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock06.c -->
