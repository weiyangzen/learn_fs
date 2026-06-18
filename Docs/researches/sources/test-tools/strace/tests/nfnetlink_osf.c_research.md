# sources/test-tools/strace/tests/nfnetlink_osf.c

Purpose: tests nfnetlink passive OS fingerprinting subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_OSF`, `NFNL_MSG_OSF_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends known OSF message headers and unknown ids to verify type-name lookup and fallback behavior.

State and persistence: no OSF signatures are modified; messages are synthetic decoder probes.

Dependencies and integration points: depends on `nfnetlink_osf.h` and strace nfnetlink xlat tables.

Risks and edge cases: small subsystem command tables are easy to regress through missing constants or incorrect packed type masks.

Test signals: output should show OSF command names and normal syscall result formatting.
