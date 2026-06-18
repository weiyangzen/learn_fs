# sources/test-tools/strace/tests/netlink_netfilter.c

Purpose: validates broad `NETLINK_NETFILTER` decoding for base nfnetlink batch messages, netfilter subsystem identifiers, nf_tables payloads, and unknown data.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_NETFILTER)`, `sendto`, `struct nlmsghdr`, `struct nfgenmsg`, `struct nfnetlink_msg`, `NFNL_MSG_BATCH_*`, `NFNL_SUBSYS_*`, `NFT_MSG_*`, `TEST_NETLINK`, `TEST_NETLINK_`, and `TEST_NETLINK_OBJECT_EX_`.

Control flow: tests header-only message types and flags, `NLMSG_DONE`, netfilter family generation messages, batch begin/end markers, nf_tables message types with `nfgenmsg`, unsupported/unknown type fallbacks, and partial object reads.

State and persistence: sends synthetic netlink buffers nonblocking over a temporary socket; it does not install nftables rules or change kernel netfilter configuration.

Dependencies and integration points: depends on Linux netfilter/nf_tables headers and strace netlink helper macros. It forms the generic base around which the more focused `nfnetlink_*` files test subsystem-specific type names.

Risks and edge cases: message type packing combines subsystem id and command id, making xlat regressions likely if masks shift. Short `nfgenmsg` reads and unknown command fallbacks are explicit boundaries.

Test signals: expected output shows nfnetlink batch names, `NFNL_SUBSYS_*`/`NFT_MSG_*` decoding, family/version/res_id fields, raw fallback, and clean exit.
