# sources/test-tools/strace/tests/lstatx.c

Purpose: `lstatx.c` is a focused strace test/helper source in the `lstat stat-structure wrapper` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 20 line(s), 524 byte(s); classification `lstat stat-structure wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `xstatx.c`. Key macros/compile switches are `TEST_SYSCALL_INVOKE`, `PRINT_SYSCALL_HEADER`, `PRINT_SYSCALL_FOOTER`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `xstatx.c`. Important compile-time knobs are `TEST_SYSCALL_INVOKE`, `PRINT_SYSCALL_HEADER`, `PRINT_SYSCALL_FOOTER`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
