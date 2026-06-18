# sources/test-tools/strace/tests/ksysent.c

Purpose: `ksysent.c` is a focused strace test/helper source in the `kernel syscall table consistency test` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 100 line(s), 2346 byte(s); classification `kernel syscall table consistency test`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `sysent.h`, `stdio.h`, `string.h`, `scno.h`, `sysent_shorthand_defs.h`, `syscallent.h`, `sysent_shorthand_undefs.h`, `ksysent.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `sysent.h`, `stdio.h`, `string.h`, `scno.h`, `sysent_shorthand_defs.h`, `syscallent.h`, `sysent_shorthand_undefs.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 5 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
