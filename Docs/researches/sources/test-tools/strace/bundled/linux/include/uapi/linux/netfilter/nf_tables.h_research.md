# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables.h

Purpose: declares the full nftables nfnetlink ABI: ruleset object message types, tables, chains, rules, sets/elements, expressions, verdict/data/register schemas, stateful objects, flowtables, trace events, and tunnel/offload metadata.

Important APIs/types/functions: key groups include `nft_registers`, `nft_verdicts`, `nf_tables_msg_types`, table/chain/rule/set attributes, expression attributes for immediate, bitwise, byteorder, cmp, range, lookup, dynset, payload, exthdr, meta, rt, socket, ct, limit, counter, log, queue, quota, nat, tproxy, masq, redir, dup/fwd, fib, osf, synproxy, xfrm, trace, ng, tunnel, plus `NFT_OBJECT_*`.

Control flow: userspace sends batched nfnetlink transactions to create/update/delete/destroy/query tables, chains, rules, sets, elements, objects, and flowtables. Packet evaluation loads data into virtual registers, executes expressions in rule order, and returns verdicts or stateful side effects.

State/persistence behavior: most messages mutate persistent per-netns nftables ruleset state. Sets may contain timeouts, intervals, expressions, object refs, and dynamic updates. Counters, quotas, limits, last-seen, flowtables, and trace state evolve with packets.

Dependencies/integration: integrates with nfnetlink, generic netfilter verdicts/hooks, conntrack, NAT, routing/FIB, sockets/cgroups, XFRM, tunnel metadata, logging/queue subsystems, and compatibility layers.

Risks and test signals: schema is large, nested, versioned, and context-sensitive. Tests should decode every message type, object kind, expression attr family, transaction IDs, owner/persist flags, dynamic set operations, trace events, reset-get messages, and deprecated fields.
