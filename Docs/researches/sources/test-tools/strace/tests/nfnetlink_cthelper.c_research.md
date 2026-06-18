# sources/test-tools/strace/tests/nfnetlink_cthelper.c

Purpose: verifies nfnetlink conntrack-helper subsystem message name and flag decoding.

Important APIs, types, and helpers: `NETLINK_NETFILTER`, `NFNL_SUBSYS_CTHELPER`, `NFNL_MSG_CTHELPER_*`, `struct nlmsghdr`, `sendto`, `create_nl_socket`, and `sprintrc`.

Control flow: sends header-only netfilter netlink messages for helper get/new/delete commands, with request/dump and create-style flags, plus unknown command coverage.

State and persistence: no helper configuration is changed because only synthetic messages are sent nonblocking through the test socket.

Dependencies and integration points: depends on `nfnetlink_cthelper.h` constants and the shared nfnetlink decoder.

Risks and edge cases: command constants may be absent or differ on older headers; flag decoding is command-context-sensitive.

Test signals: expected output contains symbolic CTHelper message names, relevant `NLM_F_*` flags, unknown fallback comments, and normal exit.
