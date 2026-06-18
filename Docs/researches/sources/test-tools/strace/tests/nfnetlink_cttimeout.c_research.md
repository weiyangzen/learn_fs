# sources/test-tools/strace/tests/nfnetlink_cttimeout.c

Purpose: tests nfnetlink conntrack-timeout subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_CTNETLINK_TIMEOUT`, `IPCTNL_MSG_TIMEOUT_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends timeout command headers with known get/new/delete/default-style message ids and flag combinations, plus unknown command coverage.

State and persistence: does not change timeout policies; all inputs are synthetic netlink headers.

Dependencies and integration points: depends on `nfnetlink_cttimeout.h` and strace’s nfnetlink message xlat handling.

Risks and edge cases: timeout command sets include extra/default messages compared with simpler nfnetlink subsystems, so table completeness is important.

Test signals: expected output should show timeout subsystem names and fallback comments for unknown ids.
