# sources/test-tools/strace/tests/lstat.c

Purpose: `lstat.c` exercises strace decoding for syscall(s) `lstat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 23 line(s), 455 byte(s); classification `lstat stat-structure wrapper`; functions none visible in this file; syscall markers `lstat`. Key includes are `tests.h`, `scno.h`, `lstatx.c`. Key macros/compile switches are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `SAMPLE_SIZE`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`lstat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `lstatx.c`. Important compile-time knobs are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `SAMPLE_SIZE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
