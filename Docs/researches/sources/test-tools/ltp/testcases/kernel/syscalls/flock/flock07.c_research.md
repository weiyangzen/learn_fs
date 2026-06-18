<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock07.c

Purpose: Checks `flock()` interactions with open modes and descriptor lifecycle edge cases. Source notes: Author: Yang Xu <xuyang2018.jy@fujitsu.com> \ Verify that flock(2) fails with errno EINTR when waiting to acquire a lock, and the call is interrupted by a signal. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (77 lines, 1428 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_TOUCH, SAFE_OPEN, SAFE_CLOSE, SAFE_SIGEMPTYSET, SAFE_SIGACTION, TST_EXP_FAIL, TST_EXP_PASS, SAFE_FORK, SAFE_KILL, SAFE_WAITPID; types/structs: struct sigaction, struct tst_test; functions: handler, setup, cleanup, child_do, verify_flock; local macros/constants: TEMPFILE.

Control flow: setup path: setup; exercise path: child_do, verify_flock; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, UID/capability-sensitive kernel state, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINTR; key constants: O_RDWR, SIGUSR1, LOCK_EX; harness metadata: .setup, .cleanup, .test_all, .needs_tmpdir, .needs_root, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock07.c -->
