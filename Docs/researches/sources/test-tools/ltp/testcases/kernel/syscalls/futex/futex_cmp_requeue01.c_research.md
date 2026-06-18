<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue01.c

Purpose: Functional `FUTEX_CMP_REQUEUE` test that forks waiters, wakes some, requeues others, and verifies final wake counts. Source notes: \ Verify the basic functionality of futex(FUTEX_CMP_REQUEUE). futex(FUTEX_CMP_REQUEUE) can wake up the number of waiters specified by val argument and then requeue the number of waiters limited by val2 argument (i.e. move some remaining waiters from uaddr to uaddr2 address). spurious wakeup or signal make sure TST_PROCESS_STATE_WAIT() can always succeed change futex value, so any spurious wakeups or signals after this point get bounced back to userspace. Wakes up a maximum of tc->set_wakes waiters. tc->set_requeues specifies an upper limit on the number of waiters that are requeued. Returns the total number of waiters that were woken up or requeued. Fail if more than requested wakes + requeues were returned SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (221 lines, 5965 bytes).

Important APIs/types/functions: calls/wrappers: futex(), TST_PROCESS_STATE_WAIT, SAFE_FORK, SAFE_WAITPID, SAFE_MMAP, SAFE_MUNMAP; types/structs: struct shared_data, struct tcase, struct futex_test_variants, struct tst_ts, struct tst_test; functions: do_child, verify_futex_cmp_requeue, setup, cleanup.

Control flow: setup path: setup; exercise path: do_child, verify_futex_cmp_requeue; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/wait.h`, `stdlib.h`, `sys/time.h`, `tst_test.h`, `futextest.h`, `lapi/futex.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN; key constants: FUTEX_CMP_REQUEUE, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_INITIALIZER; harness metadata: .setup, .cleanup, .tcnt, .test, .test_variants, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue01.c -->
