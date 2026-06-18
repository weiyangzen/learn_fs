# sources/test-tools/strace/tests/nfnetlink_queue.c

Purpose: verifies nfnetlink queue subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_QUEUE`, `NFQNL_MSG_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends representative queue message types and an unknown type through a netfilter netlink socket.

State and persistence: no packets are queued or verdicts applied; this is header-only decode coverage.

Dependencies and integration points: depends on `nfnetlink_queue.h` and strace’s nfnetlink message-name tables.

Risks and edge cases: command constants and fallback comments must match the packed subsystem/type representation.

Test signals: expected output contains `NFQNL_MSG_*` symbolic names and exits cleanly.
