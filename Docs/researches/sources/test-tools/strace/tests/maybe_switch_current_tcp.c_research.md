# sources/test-tools/strace/tests/maybe_switch_current_tcp.c

Purpose: `maybe_switch_current_tcp.c` exercises strace decoding for syscall(s) `execveat`, `gettid` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 83 line(s), 1837 byte(s); classification `thread execve/current-tcp regression test`; functions `thread`, `main`; syscall markers `execveat`, `gettid`. Key includes are `tests.h`, `errno.h`, `pthread.h`, `stdio.h`, `unistd.h`, `scno.h`. Key macros/compile switches are `QUIET_MSG`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`thread`, `main`), invokes syscall targets (`execveat`, `gettid`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `pthread.h`, `stdio.h`, `unistd.h`, `scno.h`. Important compile-time knobs are `QUIET_MSG`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
