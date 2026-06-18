# sources/test-tools/strace/tests/nfnetlink_ulog.c

Purpose: tests nfnetlink log/ulog subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_ULOG`, `NFULNL_MSG_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends known ulog/log command headers and unknown ids to verify symbolic type rendering.

State and persistence: no logging configuration is changed; synthetic headers are sent only for strace decoding.

Dependencies and integration points: uses `nfnetlink_log.h` and the shared nfnetlink decoder.

Risks and edge cases: decoder must distinguish ULOG/LOG command names from queue and nftables commands despite shared protocol packing.

Test signals: output includes `NFULNL_MSG_*` names or unknown comments and the normal exit marker.
