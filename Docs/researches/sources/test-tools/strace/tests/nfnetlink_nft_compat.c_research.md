# sources/test-tools/strace/tests/nfnetlink_nft_compat.c

Purpose: checks nf_tables compatibility subsystem message decoding for `NFNL_SUBSYS_NFT_COMPAT`.

Important APIs, types, and helpers: `NFNL_SUBSYS_NFT_COMPAT`, `NFT_MSG_COMPAT_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends compatibility get/new/delete-style header-only messages, expected flag variants, and unknown command values.

State and persistence: does not alter nftables compatibility objects; messages are decoder-only inputs.

Dependencies and integration points: depends on `nf_tables_compat.h` and strace netfilter xlat tables.

Risks and edge cases: compatibility command names overlap conceptually with nftables but live in a distinct subsystem; decoder packing must preserve that distinction.

Test signals: output should show `NFT_MSG_COMPAT_*` names under `NFNL_SUBSYS_NFT_COMPAT`, unknown fallbacks, and normal exit.
