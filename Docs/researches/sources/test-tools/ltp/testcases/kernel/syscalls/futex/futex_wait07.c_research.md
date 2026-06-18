<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait07.c

Purpose: Signal interruption test proving a blocked `FUTEX_WAIT` returns `EINTR` after parent sends `SIGUSR1`. Source notes: \ Check that futex(FUTEX_WAIT) returns EINTR when interrupted by a signal. A child process blocks on futex_wait() with a long timeout. The parent waits for the child to enter sleep state, then sends SIGUSR1 to it. The child verifies it received EINTR and exits accordingly. Empty handler: receiving the signal is sufficient to interrupt futex_wait(). SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (89 lines, 2185 bytes).

Important APIs/types/functions: calls/wrappers: futex(), SAFE_SIGEMPTYSET, SAFE_SIGACTION, TST_EXP_FAIL, SAFE_FORK, TST_PROCESS_STATE_WAIT, SAFE_KILL, SAFE_WAITPID, SAFE_MMAP, SAFE_MUNMAP; types/structs: struct futex_test_variants, struct sigaction, struct tst_ts, struct tst_test; functions: sigusr1_handler, run, setup, cleanup.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `signal.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; errno checks: EINTR; key constants: FUTEX_WAIT, SIGUSR1, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_INITIALIZER; harness metadata: .setup, .cleanup, .test_all, .test_variants, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait07.c -->
