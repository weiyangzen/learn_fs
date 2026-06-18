# sources/test-tools/strace/tests/lsm_list_modules.c

Purpose: `lsm_list_modules.c` exercises strace decoding for syscall(s) `lsm_list_modules` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 106 line(s), 2877 byte(s); classification `LSM syscall decoder exercise`; functions `k_lsm_list_modules`, `main`; syscall markers `lsm_list_modules`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Key macros/compile switches are `INJ_STR`, `INJ_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_lsm_list_modules`, `main`), invokes syscall targets (`lsm_list_modules`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 3 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Important compile-time knobs are `INJ_STR`, `INJ_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, LSM UAPI.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 9 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
