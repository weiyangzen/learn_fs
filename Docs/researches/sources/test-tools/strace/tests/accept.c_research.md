<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/accept.c -->
## sources/test-tools/strace/tests/accept.c

Purpose: Tests decoding of `accept`-style socket syscalls, including direct `__NR_accept` and legacy `socketcall` routing.

Important APIs/types/functions: Defines `TEST_SYSCALL_NAME`, `TEST_SYSCALL_STR`, `do_accept`, `TEST_SYSCALL_PREPARE`, `connect_un`, and includes `sockname.c`. Uses Unix-domain sockets, `bind`, `listen`, `connect`, and `test_sockname_syscall`.

Control flow: Selects direct `accept` or socketcall implementation, creates a listening Unix socket, prepares a client connection in `connect_un`, delegates the actual bad/good sockaddr decoding cases to `sockname.c`, then cleans up the test socket.

State and persistence: Creates and unlinks `TEST_SOCKET` and `TEST_SOCKET.connect`; no state remains after cleanup.

Dependencies and integration: Reused by `accept4.c` through `TEST_SYSCALL_NAME`/suffix macros. Depends on `sockname.c` for common accept/getsockname-style assertions.

Risks: Unix socket filesystem cleanup and connection timing can fail in restricted environments. Legacy socketcall coverage depends on architecture availability.

Test signals: Expected output includes decoded `accept` calls, sockaddr/socklen handling, return status, and final clean exit; missing syscalls should produce a skip binary.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/accept.c -->
