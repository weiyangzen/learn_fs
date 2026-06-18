# sources/test-tools/strace/tests/nfnetlink_ipset.c

Purpose: verifies nfnetlink ipset subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_IPSET`, `IPSET_CMD_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends representative ipset command headers and unknown command ids to ensure symbolic and fallback type printing.

State and persistence: no ipsets are created, listed, or destroyed; the socket sends synthetic messages only.

Dependencies and integration points: uses `linux/netfilter/ipset/ip_set.h` and strace nfnetlink decoding.

Risks and edge cases: ipset command tables vary across kernels; unknown fallback formatting must remain deterministic.

Test signals: expected output decodes packed `NFNL_SUBSYS_IPSET` command values and exits normally.
