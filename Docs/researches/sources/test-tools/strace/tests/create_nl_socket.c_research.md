# sources/test-tools/strace/tests/create_nl_socket.c

Purpose: `create_nl_socket.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `create_nl_socket_ext`; macros include none detected; included headers include `tests.h`, `sys/socket.h`, `netlink.h`. Kernel/user ABI names observed in the full file include `socket`. Prominent constants include `SPDX`, `GPL`, `AF_NETLINK`, `SOCK_RAW`, `SOL_SOCKET`, `SO_ACCEPTCONN`; prominent struct names include `sockaddr_nl`, `sockaddr`.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `sys/socket.h`, `netlink.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 33 lines, 858 bytes, sha256 prefix `813c514977e0`.
