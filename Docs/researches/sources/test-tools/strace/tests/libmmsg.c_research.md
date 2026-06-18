# sources/test-tools/strace/tests/libmmsg.c

Purpose: `libmmsg.c` exercises strace decoding for syscall(s) `recvmmsg`, `sendmmsg` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 50 line(s), 1076 byte(s); classification `test helper library`; functions `recv_mmsg`, `send_mmsg`; syscall markers `recvmmsg`, `sendmmsg`. Key includes are `tests.h`, `errno.h`, `scno.h`. Key macros/compile switches are `__NR_recvmmsg`, `SC_recvmmsg`, `__NR_sendmmsg`, `SC_sendmmsg`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`recv_mmsg`, `send_mmsg`), invokes syscall targets (`recvmmsg`, `sendmmsg`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `scno.h`. Important compile-time knobs are `__NR_recvmmsg`, `SC_recvmmsg`, `__NR_sendmmsg`, `SC_sendmmsg`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
