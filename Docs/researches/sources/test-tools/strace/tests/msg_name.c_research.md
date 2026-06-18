# sources/test-tools/strace/tests/msg_name.c

Purpose: `msg_name.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 160 line(s), 5172 byte(s); classification `recvmsg address-name decoder exercise`; functions `send_recv`, `test_msg_name`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`. Key macros/compile switches are `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`send_recv`, `test_msg_name`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`. Important compile-time knobs are `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 9 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
