# sources/test-tools/strace/tests/nanosleep.c

Purpose: `nanosleep.c` exercises strace decoding for syscall(s) `nanosleep` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 132 line(s), 3688 byte(s); classification `nanosleep interrupted-time decoder exercise`; functions `k_nanosleep`, `handler`, `main`; syscall markers `nanosleep`. Key includes are `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `stdint.h`, `signal.h`, `sys/time.h`, `unistd.h`, `kernel_old_timespec.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_nanosleep`, `handler`, `main`), invokes syscall targets (`nanosleep`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `stdint.h`, `signal.h`, `sys/time.h`, `unistd.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 10 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
