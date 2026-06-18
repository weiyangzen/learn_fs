<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait06.c

Purpose: Negative `FUTEX_WAIT` coverage for bad futex address and bad timeout pointer returning `EFAULT`. Source notes: \ Check that futex(FUTEX_WAIT) returns EFAULT when: 1) uaddr points to unmapped memory 2) timeout points to unmapped memory SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (73 lines, 1801 bytes).

Important APIs/types/functions: calls/wrappers: futex(), TST_EXP_FAIL; types/structs: struct futex_test_variants, struct testcase, struct tst_ts, struct tst_test; functions: run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/mman.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose; bad-address tests are ABI-sensitive.

Test signals: explicit failure reporting; errno checks: EFAULT; key constants: FUTEX_WAIT, FUTEX_INITIALIZER, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .test, .tcnt, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait06.c -->
