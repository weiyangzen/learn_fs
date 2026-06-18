<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock03.c

Purpose: Fork-based `flock()` inheritance and mutual exclusion coverage between parent and child descriptors. Source notes: \ Verify that flock(2) cannot unlock a file locked by another task. Fork a child processes. The parent flocks a file with LOCK_EX. Child waits for that to happen, then checks to make sure it is locked. Child then tries to unlock the file. If the unlock succeeds, the child attempts to lock the file with LOCK_EX. The test passes if the child is able to lock the file. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (97 lines, 2102 bytes).

Important APIs/types/functions: calls/wrappers: flock(), TST_CHECKPOINT_WAIT, SAFE_OPEN, SAFE_CLOSE, SAFE_FORK, TST_CHECKPOINT_WAKE; types/structs: struct tst_test; functions: childfunc, verify_flock, setup.

Control flow: setup path: setup; exercise path: childfunc, verify_flock; notable execution mechanics: forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `stdlib.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: LOCK_EX, O_RDWR, LOCK_NB, LOCK_UN, O_CREAT, O_TRUNC; harness metadata: .test_all, .needs_checkpoints, .forks_child, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock03.c -->
