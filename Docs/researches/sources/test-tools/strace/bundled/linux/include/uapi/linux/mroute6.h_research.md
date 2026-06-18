# sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute6.h

Purpose: defines IPv6 multicast routing ABI analogous to `mroute.h`, including MIF management, forwarding cache structs, counter ioctls, MRT6 control messages, and netlink cache report attributes.

Important APIs/types/functions: exports `MRT6_*` commands, `SIOCGETMIFCNT_IN6`, `SIOCGETSGCNT_IN6`, flush flags, `mifbitmap_t`, `mifi_t`, `if_set` macros, `mif6ctl`, `mf6cctl`, `sioc_sg_req6`, `sioc_mif_req6`, `mrt6msg`, `MRT6MSG_*`, and `IP6MRA_CREPORT_*`.

Control flow: IPv6 multicast routing daemons enable MRT6, add/delete MIFs and forwarding cache entries, receive MLD/PIM control payloads, query counters, select tables, and flush entries/interfaces.

State/persistence behavior: mutates per-netns IPv6 multicast routing state, MIFs, cache entries, and counters. Query ioctls and cache reports observe live state.

Dependencies/integration: depends on Linux constants/types/sockios and IPv6 sockaddr definitions. Integrates with PIM6/MLD daemons, raw IPv6 sockets, and rtnetlink.

Risks and test signals: `if_set` bitmap sizing and IPv6 sockaddr layouts must be decoded correctly. Tests should cover MRT6 commands, MIF flags, counter structs, `mrt6msg` packet reports, and IP6MRA attributes.
