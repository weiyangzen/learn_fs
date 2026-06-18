<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate04.c

Purpose: Mandatory locking regression test: parent `ftruncate()` calls fail inside/before a child-held lock and succeed after the child releases it. Source notes: Robbie Williamson <robbiew@us.ibm.com> Roy Lee <roylee@andestech.com> Test Description: Tests truncate and mandatory record locking. Parent creates a file, child locks a region and sleeps. Parent checks that ftruncate before the locked region and inside the region fails while ftruncate after the region succeds. Parent wakes up child, child exits, lock is unlocked. Parent checks that ftruncate now works in all cases. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (182 lines, 3920 bytes).

Important APIs/types/functions: calls/wrappers: fstat(), ftruncate(), mount(), SAFE_FSTAT, TST_CHECKPOINT_WAIT, SAFE_OPEN, TST_CHECKPOINT_WAKE, SAFE_WAIT, SAFE_CLOSE, SAFE_FCNTL, TST_CHECKPOINT_WAKE_AND_WAIT, SAFE_CHMOD, SAFE_FORK; types/structs: struct stat, struct flock, struct tst_test; functions: ftruncate_expect_fail, ftruncate_expect_success, doparent, dochild, verify_ftruncate, setup; local macros/constants: RECLEN, MNTPOINT, TESTFILE.

Control flow: setup path: setup; exercise path: ftruncate_expect_fail, ftruncate_expect_success, doparent, dochild, verify_ftruncate; notable execution mechanics: forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, UID/capability-sensitive kernel state, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `errno.h`, `sys/types.h`, `sys/stat.h`, `sys/mount.h`, `unistd.h`, `stdlib.h`, `sys/statvfs.h`, `tst_test.h`; integrates with the LTP ftruncate syscall suite; uses the LTP C harness and result macros; declares kernel configuration requirements.

Risks: requires root/capability-sensitive behavior; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN, EPERM; key constants: O_RDWR, O_NONBLOCK, F_WRLCK, F_SETLKW; harness metadata: .needs_kconfigs, .test_all, .setup, .needs_checkpoints, .forks_child, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ftruncate/ftruncate04.c -->
