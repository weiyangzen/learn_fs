# sources/test-tools/strace/tests/nfnetlink_ctnetlink.c

Purpose: validates nfnetlink conntrack subsystem message decoding for `NFNL_SUBSYS_CTNETLINK`.

Important APIs, types, and helpers: `NFNL_SUBSYS_CTNETLINK`, `IPCTNL_MSG_CT_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends known conntrack command headers, combines them with request/dump/create/delete flags, and includes unknown command values for fallback coverage.

State and persistence: does not manipulate real conntrack entries; all messages are test buffers.

Dependencies and integration points: depends on `nfnetlink_conntrack.h` and strace nfnetlink xlat tables.

Risks and edge cases: conntrack command name coverage is sensitive to kernel UAPI evolution and strace xlat synchronization.

Test signals: expected output shows packed subsystem/type names for conntrack commands and stable syscall return formatting.
