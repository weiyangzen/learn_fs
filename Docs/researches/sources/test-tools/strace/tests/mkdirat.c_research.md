# sources/test-tools/strace/tests/mkdirat.c

Purpose: `mkdirat.c` exercises strace decoding for syscall(s) `mkdirat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 18 line(s), 413 byte(s); classification `mkdir mode wrapper`; functions none visible in this file; syscall markers `mkdirat`. Key includes are `tests.h`, `scno.h`, `umode_t.c`. Key macros/compile switches are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_SYSCALL_PREFIX_ARGS`, `TEST_SYSCALL_PREFIX_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`mkdirat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `umode_t.c`. Important compile-time knobs are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_SYSCALL_PREFIX_ARGS`, `TEST_SYSCALL_PREFIX_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
