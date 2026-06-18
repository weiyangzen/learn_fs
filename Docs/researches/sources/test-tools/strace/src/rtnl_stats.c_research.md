# sources/test-tools/strace/src/rtnl_stats.c

Purpose: Decodes route-netlink interface statistics messages and nested xstats/offload/AF-specific stats.

Important APIs/types/functions: `decode_ifstatsmsg`, bridge VLAN/mcast/STP xstats decoders, bond 802.3ad stats decoders, offload stats, MPLS link stats, and `ifstatsmsg_nla_decoders`.

Control flow: fixed `if_stats_msg` prints family, optional padding if nonzero, ifindex, and filter mask. Attributes dispatch to link stats64, bridge/bond xstats, offload stats, or AF_SPEC; nested bridge/bond/MPLS tables decode fixed structs and append hex tail data when payload is larger than known struct.

State and persistence: stateless.

Dependencies/integration: Linux bonding/bridge/MPLS/rtnetlink headers, nlattr helpers, shared `decode_nla_rtnl_link_stats64` from link decoder, and many stats xlat tables.

Risks: stats structs can grow; code preserves tail bytes for several fixed structs. Array-indexed multicast stats depend on index xlat table alignment.

Test signals: RTM_GETSTATS with link64, bridge VLAN/mcast/STP xstats, bond 3ad, offload CPU hit, MPLS stats, nonzero padding, and extended payload tails.
