# sources/test-tools/strace/bundled/linux/include/uapi/linux/neighbour.h

Purpose: declares rtnetlink ABI for neighbor cache entries, neighbor table parameters/statistics, bridge FDB extended attributes, flags, and state constants.

Important APIs/types/functions: core types are `ndmsg`, `nda_cacheinfo`, `ndt_stats`, `ndtmsg`, and `ndt_config`. Attribute enums include `NDA_*`, `NDTPA_*`, `NDTA_*`, and `NFEA_*`. Flags cover `NTF_*`, extended flags, and `NUD_*` states.

Control flow: userspace sends RTM neighbor messages to add/delete/query ARP/NDP/FDB entries and RTM_GET/SETNEIGHTBL for table configuration. Dumps may span multiple messages with global and per-device parameter sets.

State/persistence behavior: neighbor entries and table parameters are kernel networking state with aging, probing, garbage collection, offload, external-learning, locked, managed, and permanent behaviors. Counters/statistics update with neighbor activity.

Dependencies/integration: depends on Linux netlink and type headers. Integrates with ARP, IPv6 NDP, bridge FDB, routing, switchdev/offload, and user control planes.

Risks and test signals: many flags alter aging and deletion semantics. Tests should decode `ndmsg`, cacheinfo, NUD states, extended FDB attrs, table stats/config, per-device parms, and masks for state/flags updates.
