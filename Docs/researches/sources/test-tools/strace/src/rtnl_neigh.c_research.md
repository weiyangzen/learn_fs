# sources/test-tools/strace/src/rtnl_neigh.c

Purpose: Decodes neighbor table route-netlink messages (`ndmsg`) and neighbor attributes.

Important APIs/types/functions: `decode_ndmsg`, neighbor address/cacheinfo decoders, and attr tables for `NDA_*` plus FDB extended attrs.

Control flow: prints fixed neighbor header fields including family, ifindex, state, flags, and type, then decodes attrs. Address decoding uses `ndm_family`; cacheinfo and probes/config attrs decode fixed structs/scalars.

State and persistence: stateless with fixed header passed as opaque context.

Dependencies/integration: Linux `neighbour.h`, netlink/nlattr helpers, neighbor state/flag/type xlat tables, FDB notify/extended flag xlat.

Risks: neighbor attrs vary by address family and bridge/FDB context. Unknown or short attrs must be rejected to generic output without corrupting array formatting.

Test signals: IPv4/IPv6 neighbor entries, bridge FDB entries, cacheinfo, protocol/vlan attrs, extended flags, malformed attrs.
