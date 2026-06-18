# sources/test-tools/strace/tests/linkat.c

Purpose: `linkat.c` exercises strace decoding for syscall(s) `linkat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 288 line(s), 8701 byte(s); classification `linkat path and flag decoder exercise`; functions `mangle_secontext_field`, `main`; syscall markers `linkat`. Key includes are `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, `string.h`, `secontext.h`, ... (12 total). Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`mangle_secontext_field`, `main`), invokes syscall targets (`linkat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, ... (12 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, allocation helpers, SELinux context helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 14 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
