# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_conntrack.h

Purpose: defines conntrack and expectation nfnetlink ABI for creating, querying, deleting, dumping, filtering, and reporting connection tracking state.

Important APIs/types/functions: message enums cover CT and expectation operations plus stats/dying/unconfirmed dumps. Attribute groups describe tuples, IP addresses, L4 protocol fields, TCP/DCCP/SCTP protoinfo, counters, timestamps, NAT/protonat, sequence adjustment, synproxy, expectations, helper info, security context, per-CPU/global/expect stats, and filters.

Control flow: userspace sends ctnetlink messages to create/query/delete conntracks or expectations, optionally filter by tuple/status/marks/labels, retrieve stats, and receive multicast lifecycle events.

State/persistence behavior: conntrack entries, expectations, counters, NAT mapping, marks, labels, helper state, timestamps, and timeouts are mutable per-netns state. Counter-reset and delete operations have side effects.

Dependencies/integration: includes `nfnetlink.h`; integrates with netfilter hooks, NAT, helpers, labels, secctx, synproxy, and nftables `ct` expressions.

Risks and test signals: nested tuple direction and protocol-specific attrs are context-dependent. Tests should decode original/reply tuples, NAT aliases, 64-bit counters, timestamp events, expectation NAT, status masks, labels/masks, and stats messages.
