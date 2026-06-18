<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait03.c

Purpose: Threaded private `FUTEX_WAIT` wakeup test using pthread synchronization and `FUTEX_PRIVATE_FLAG`. Source notes: Block on a futex and wait for wakeup. This tests uses private mutexes with threads. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (71 lines, 1669 bytes).

Important APIs/types/functions: calls/wrappers: TST_PROCESS_STATE_WAIT, SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN; types/structs: struct futex_test_variants, struct tst_test; functions: threaded, run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants, uses pthread workers for concurrent access.

State and persistence behavior: The test manipulates threads and shared in-process synchronization, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `futextest.h`, `futex_utils.h`, `tst_safe_pthread.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: FUTEX_INITIALIZER, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_PRIVATE_FLAG; harness metadata: .setup, .test_all, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait03.c -->
