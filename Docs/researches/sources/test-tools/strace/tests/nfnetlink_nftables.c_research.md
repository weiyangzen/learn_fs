# sources/test-tools/strace/tests/nfnetlink_nftables.c

Purpose: validates nf_tables nfnetlink message type decoding for `NFNL_SUBSYS_NFTABLES`.

Important APIs, types, and helpers: `NFNL_SUBSYS_NFTABLES`, `NFT_MSG_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: emits header-only nftables commands across known message names and common request/dump/create/delete flags, plus unknown command slots.

State and persistence: does not create or modify nftables tables/chains/rules. It only feeds synthetic messages to strace.

Dependencies and integration points: uses `nf_tables.h` and the strace nfnetlink/nftables xlat tables.

Risks and edge cases: nftables UAPI evolves regularly, so command-name tables and unknown fallback behavior are important.

Test signals: expected trace contains packed nftables message names with correct flag rendering and the exit marker.
