# sources/test-tools/strace/tests/mmsg_name.c

Purpose: `mmsg_name.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 219 line(s), 5771 byte(s); classification `mmsg socket-message decoder exercise`; functions `print_msghdr`, `test_mmsg_name`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `errno.h`, `limits.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/un.h`, `msghdr.h`. Key macros/compile switches are `IOV_MAX1`, `TEST_NAME`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_msghdr`, `test_mmsg_name`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 6 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `limits.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/un.h`, ... (9 total). Important compile-time knobs are `IOV_MAX1`, `TEST_NAME`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, message-header helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 30 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
