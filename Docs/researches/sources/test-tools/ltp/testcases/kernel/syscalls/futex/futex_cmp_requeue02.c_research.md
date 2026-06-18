<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue02.c

Purpose: Negative `FUTEX_CMP_REQUEUE` and CVE-2018-6927 regression test for invalid wake/requeue counts and compare mismatches. Source notes: Description: Check various errnos for futex(FUTEX_CMP_REQUEUE). 1) futex(FUTEX_CMP_REQUEUE) with invalid val returns EINVAL. 2) futex(FUTEX_CMP_REQUEUE) with invalid val2 returns EINVAL. 3) futex(FUTEX_CMP_REQUEUE) with mismatched val3 returns EAGAIN. It's also a regression test for CVE-2018-6927: fbe0e839d1e2 ("futex: Prevent overflow by strengthen input validation") SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (98 lines, 2517 bytes).

Important APIs/types/functions: calls/wrappers: futex(), SAFE_MMAP, SAFE_MUNMAP; types/structs: struct tcase, struct futex_test_variants, struct tst_test, struct tst_tag; functions: verify_futex_cmp_requeue, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_futex_cmp_requeue; cleanup path: cleanup; notable execution mechanics: runs across syscall ABI variants, iterates a case table.

State and persistence behavior: The test manipulates shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/time.h`, `tst_test.h`, `futextest.h`, `lapi/futex.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EAGAIN; key constants: FUTEX_CMP_REQUEUE, FUTEX_INITIALIZER, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .cleanup, .test, .tcnt, .test_variants, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_cmp_requeue02.c -->
