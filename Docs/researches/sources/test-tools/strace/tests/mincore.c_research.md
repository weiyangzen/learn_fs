# sources/test-tools/strace/tests/mincore.c

Purpose: `mincore.c` is a focused strace test/helper source in the `mincore decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 58 line(s), 1255 byte(s); classification `mincore decoder exercise`; functions `print_mincore`, `test_mincore`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `sys/mman.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_mincore`, `test_mincore`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `sys/mman.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 7 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
