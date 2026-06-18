# sources/test-tools/strace/tests/memfd_create.c

Purpose: `memfd_create.c` exercises strace decoding for syscall(s) `memfd_create` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 96 line(s), 2349 byte(s); classification `memfd_create decoder exercise`; functions `k_memfd_create`, `main`; syscall markers `memfd_create`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/memfd.h`. Key macros/compile switches are `flags1_str`, `memfd_create_fmt`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_memfd_create`, `main`), invokes syscall targets (`memfd_create`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/memfd.h`. Important compile-time knobs are `flags1_str`, `memfd_create_fmt`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 8 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
