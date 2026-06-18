# sources/test-tools/strace/tests/landlock_add_rule.c

Purpose: `landlock_add_rule.c` exercises strace decoding for syscall(s) `landlock_add_rule` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 150 line(s), 4815 byte(s); classification `Landlock syscall decoder exercise`; functions `sys_landlock_add_rule`, `main`; syscall markers `landlock_add_rule`. Key includes are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/landlock.h`. Key macros/compile switches are `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_STR`, `RULESET_FD`, `RULESET_FD_STR`, `PARENT_FD`, `PARENT_FD_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`sys_landlock_add_rule`, `main`), invokes syscall targets (`landlock_add_rule`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 4 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/landlock.h`. Important compile-time knobs are `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_STR`, `RULESET_FD`, `RULESET_FD_STR`, `PARENT_FD`, `PARENT_FD_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, Landlock UAPI.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 8 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
