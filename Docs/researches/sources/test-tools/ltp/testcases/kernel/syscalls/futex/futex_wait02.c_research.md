<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait02.c

Purpose: Fork-based `FUTEX_WAIT` wakeup test using a shared mmap futex and child `futex_wake()`. Source notes: Block on a futex and wait for wakeup. This tests uses shared memory page to store the mutex variable. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (80 lines, 1702 bytes).

Important APIs/types/functions: calls/wrappers: TST_PROCESS_STATE_WAIT, SAFE_FORK, SAFE_WAIT, SAFE_MMAP; types/structs: struct futex_test_variants, struct tst_test; functions: do_child, run, setup.

Control flow: setup path: setup; exercise path: do_child, run; notable execution mechanics: runs across syscall ABI variants, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/mman.h`, `sys/wait.h`, `futextest.h`, `futex_utils.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64, FUTEX_INITIALIZER; harness metadata: .setup, .test_all, .test_variants, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait02.c -->
