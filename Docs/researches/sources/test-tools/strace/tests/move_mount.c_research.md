# sources/test-tools/strace/tests/move_mount.c

Purpose: `move_mount.c` exercises strace decoding for syscall(s) `move_mount` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 120 line(s), 4003 byte(s); classification `move_mount decoder exercise`; functions `k_move_mount`, `main`; syscall markers `move_mount`. Key includes are `tests.h`, `scno.h`, `fcntl.h`, `limits.h`, `stdio.h`, `stdint.h`, `unistd.h`. Key macros/compile switches are `f_flags_str`, `t_flags_str`, `set_group_str`, `beneath_str`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_move_mount`, `main`), invokes syscall targets (`move_mount`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries; temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `fcntl.h`, `limits.h`, `stdio.h`, `stdint.h`, `unistd.h`. Important compile-time knobs are `f_flags_str`, `t_flags_str`, `set_group_str`, `beneath_str`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: path filtering changes which syscall lines are expected; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 12 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, path-qualified trace filtering. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
