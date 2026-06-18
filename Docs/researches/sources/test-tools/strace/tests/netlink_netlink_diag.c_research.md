# sources/test-tools/strace/tests/netlink_netlink_diag.c

Purpose: receives and validates netlink diagnostic messages for netlink sockets, exercising decoder handling of `struct netlink_diag_msg` response data.

Important APIs, types, and helpers: `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, `bind`, `recvfrom`, `struct netlink_diag_req`, `struct netlink_diag_msg`, `NETLINK_SOCK_DIAG`, `SOCK_DIAG_BY_FAMILY`, and netlink/sock_diag headers.

Control flow: the test opens and binds a netlink socket to create a target, opens a sock_diag netlink fd, sends a request for netlink socket diagnostics, then reads decoded responses using local helper logic.

State and persistence: all sockets are transient. The bound netlink socket exists only to provide predictable diagnostic output.

Dependencies and integration points: depends on sock_diag support for netlink sockets and strace receive-side netlink diag decoding. It complements send-side netlink diagnostic structure tests.

Risks and edge cases: kernel-specific diagnostic fields, port ids, cookies, and response ordering can vary; the controlled socket setup mitigates this but still relies on kernel support.

Test signals: expected trace should include creation/bind of the target netlink socket and decoded `NETLINK_DIAG` response messages, with normal exit or skip for unavailable support.
