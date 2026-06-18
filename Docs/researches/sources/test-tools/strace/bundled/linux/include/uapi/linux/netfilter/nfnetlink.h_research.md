# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink.h

Purpose: defines the common nfnetlink envelope ABI for netfilter netlink subsystems, multicast groups, subsystem/message ID splitting, batch messages, and the common `nfgenmsg` header.

Important APIs/types/functions: exports `enum nfnetlink_groups`, `struct nfgenmsg`, `NFNETLINK_V0`, `NFNL_SUBSYS_ID`, `NFNL_MSG_TYPE`, subsystem IDs for conntrack, queue, ulog, osf, ipset, acct, cttimeout, cthelper, nftables, compat, hook, and batch begin/end attributes.

Control flow: netfilter netlink messages carry `nfgenmsg` after `nlmsghdr`; high message-type bits select subsystem and low bits select subsystem operation. Batches use reserved begin/end messages and optional generation ID.

State/persistence behavior: common header is declarative. Batch boundaries coordinate atomic changes in subsystem state such as nftables transactions.

Dependencies/integration: includes `nfnetlink_compat.h` and Linux types. Every netfilter UAPI in this subset depends on this framing directly or conceptually.

Risks and test signals: subsystem/type bit splitting must be exact. Tests should cover multicast group names/numbers, `nfgenmsg` decoding, batch begin/end, generation IDs, and every `NFNL_SUBSYS_*` mapping.
