# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/ipset/ip_set.h

Purpose: defines ipset netfilter userspace ABI for protocol negotiation, set lifecycle, element add/delete/test, save/list/header/type operations, errors, flags, counters, and legacy socket interface.

Important APIs/types/functions: includes `IPSET_PROTOCOL`, command enum `ipset_cmd`, command/create/ADT/IP-address attributes, `enum ipset_errno`, command/CADT/create flags, `ip_set_id_t`, set dimension/kopt flags, counter match structs, `SO_IP_SET`, name/index union, and `ip_set_req_*` legacy structs.

Control flow: userspace sends nfnetlink ipset commands to create/destroy/flush/rename/swap/list/save sets and add/delete/test elements. Legacy iptables paths use getsockopt operations to resolve set names/indexes and kernel protocol version.

State/persistence behavior: commands mutate named set objects, elements, counters, comments, skb marks/prio/queue metadata, timeouts, and references in the network namespace. Listing and test commands are observational except counter side effects may be skipped by flags.

Dependencies/integration: depends on Linux types and netfilter nfnetlink subsystem ID `IPSET`. Integrates with iptables/nftables matches and set-type implementations.

Risks and test signals: attribute spaces overlap by command context and many flags are split across lower/upper halves. Tests should decode protocol attrs, restore line numbers, counter matches, comments, skbinfo, legacy `SO_IP_SET`, and type-specific error bases.
