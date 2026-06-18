# sources/test-tools/strace/tests/netlink_audit.c

Purpose: verifies decoding of audit netlink message headers, specifically `AUDIT_GET` with request flags and pid namespace-aware `nlmsg_pid` rendering.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_AUDIT)`, `sendto`, `struct nlmsghdr`, `AUDIT_GET`, `NLM_F_REQUEST`, `getpid`, `PIDNS_TEST_INIT`, `pidns_print_leader`, and `pidns_pid2str`.

Control flow: `main` skips if `/proc/self/fd/` is unavailable, creates an audit netlink socket, then `test_nlmsg_type` sends one header-only audit request and prints the decoded netlink header.

State and persistence: the only state is an open netlink fd during the test and the current pid value embedded in the message header. No durable audit configuration is changed because the payload is just a test request sent nonblocking.

Dependencies and integration points: depends on Linux audit netlink headers and strace’s pid namespace test support. The file is included by the pidns translation wrapper for alternate expected output.

Risks and edge cases: audit netlink availability and permission behavior may vary, but the expected result is captured via `sprintrc`. Pid rendering must stay synchronized with namespace helper expectations.

Test signals: output should show `nlmsg_type=AUDIT_GET`, `nlmsg_flags=NLM_F_REQUEST`, the pid field, and the exit marker.
