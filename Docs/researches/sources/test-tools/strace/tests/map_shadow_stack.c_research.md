# sources/test-tools/strace/tests/map_shadow_stack.c

Purpose: `map_shadow_stack.c` exercises strace decoding for syscall(s) `map_shadow_stack` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 70 line(s), 1705 byte(s); classification `map_shadow_stack decoder exercise`; functions `k_map_shadow_stack`, `main`; syscall markers `map_shadow_stack`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_map_shadow_stack`, `main`), invokes syscall targets (`map_shadow_stack`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
