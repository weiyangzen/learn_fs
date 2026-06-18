# sources/test-tools/strace/tests/mq.c

Purpose: `mq.c` is a focused strace test/helper source in the `POSIX message-queue open/attribute test` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 60 line(s), 1418 byte(s); classification `POSIX message-queue open/attribute test`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `fcntl.h`, `mqueue.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, `xmalloc.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `fcntl.h`, `mqueue.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, `xmalloc.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, allocation helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 6 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
