# sources/test-tools/strace/tests/netlink_inet_diag.c

Purpose: exercises receive-side decoding for `NETLINK_INET_DIAG` by creating a real TCP listener and reading diagnostic netlink responses.

Important APIs, types, and helpers: `socket(AF_INET, SOCK_STREAM)`, `bind`, `listen`-style setup through fd 0, `socket(AF_NETLINK, SOCK_RAW, NETLINK_INET_DIAG)`, `sendto`/request helpers, `recvfrom`, `struct inet_diag_req_v2`, `struct inet_diag_msg`, `NETLINK_INET_DIAG`, and `inet_diag` UAPI headers.

Control flow: setup creates an IPv4 loopback TCP socket, binds it, creates a netlink inet diag socket, sends a diagnostic request, then receives and prints decoded response messages, including normal and truncated cases handled by helper functions.

State and persistence: runtime state is a loopback TCP socket and a netlink diagnostic socket. No filesystem or durable network configuration is modified.

Dependencies and integration points: depends on inet diag kernel support, loopback TCP, and strace’s netlink receive decoder. It complements send-side `netlink_sock_diag.c` by validating responses from the kernel.

Risks and edge cases: kernel response contents can vary with inet diag implementation, permissions, or socket state. The test uses controlled local sockets to reduce nondeterminism, but receive buffer length and errno handling remain important.

Test signals: expected traces include socket setup, netlink request/response decoding for inet diag structures, and successful exit or skip when required protocols are unavailable.
