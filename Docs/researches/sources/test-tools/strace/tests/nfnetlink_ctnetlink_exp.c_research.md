# sources/test-tools/strace/tests/nfnetlink_ctnetlink_exp.c

Purpose: checks nfnetlink conntrack expectation subsystem message decoding for `NFNL_SUBSYS_CTNETLINK_EXP`.

Important APIs, types, and helpers: `NFNL_SUBSYS_CTNETLINK_EXP`, expectation `IPCTNL_MSG_EXP_*` constants, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends header-only expectation netlink messages across known commands, flag combinations, and unknown command values.

State and persistence: no conntrack expectations are installed or modified; messages are nonblocking synthetic decoder inputs.

Dependencies and integration points: shares `nfnetlink_conntrack.h` with the base conntrack test and targets strace’s subsystem-specific message table.

Risks and edge cases: packed type decoding must distinguish CT and CT_EXP subsystems even when command names are similar.

Test signals: expected output has expectation-specific symbolic names, request/dump/create flags where appropriate, and clean exit.
