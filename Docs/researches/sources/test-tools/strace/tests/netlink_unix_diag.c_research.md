# sources/test-tools/strace/tests/netlink_unix_diag.c

Purpose: receives and validates UNIX socket diagnostic netlink responses for a controlled UNIX stream socket.

Important APIs, types, and helpers: `socket(AF_UNIX, SOCK_STREAM)`, `bind`, `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, `sendto`/request construction, `recvfrom`, `struct unix_diag_req`, `struct unix_diag_msg`, `UNIX_DIAG_*`, `SOCK_DIAG_BY_FAMILY`, and `assert`.

Control flow: the test creates and binds a UNIX socket path, opens a sock_diag netlink fd, sends a request for UNIX diag data, and receives decoded responses using local helper functions for normal and edge response payloads.

State and persistence: creates a temporary `netlink_unix_diag_socket` pathname and socket state. Cleanup/close semantics are expected to leave no durable state.

Dependencies and integration points: depends on UNIX socket support, sock_diag support for AF_UNIX, and strace receive-side netlink decoder logic.

Risks and edge cases: response fields such as inode/cookie and available attributes can vary by kernel. The controlled pathname helps stabilize name decoding, but missing sock_diag support should be handled by skip/failure paths.

Test signals: expected trace includes controlled socket setup and decoded `unix_diag_msg` responses with UNIX-specific fields and attributes.
