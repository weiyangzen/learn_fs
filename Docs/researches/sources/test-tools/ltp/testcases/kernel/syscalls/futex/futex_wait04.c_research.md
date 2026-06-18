<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait04.c

Purpose: Zero-page/uninitialized mapping regression test expecting `FUTEX_WAIT` on a mismatched value to return immediately. Source notes: Based on futextest (futext_wait_uninitialized_heap.c) written by KOSAKI Motohiro <kosaki.motohiro@jp.fujitsu.com> Wait on uninitialized heap. It shold be zero and FUTEX_WAIT should return immediately. This test tests zero page handling in futex code. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (58 lines, 1614 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_MMAP, SAFE_MUNMAP; types/structs: struct futex_test_variants, struct tst_ts, struct tst_test; functions: run, setup.

Control flow: setup path: setup; exercise path: run; notable execution mechanics: runs across syscall ABI variants.

State and persistence behavior: The test manipulates shared or anonymous memory mappings, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `futextest.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EWOULDBLOCK; key constants: FUTEX_WAIT, __NR_futex, FUTEX_FN_FUTEX, __NR_futex_time64, FUTEX_FN_FUTEX64; harness metadata: .setup, .test_all, .test_variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait04.c -->
