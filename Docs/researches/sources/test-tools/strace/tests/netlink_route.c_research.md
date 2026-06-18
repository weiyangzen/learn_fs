# sources/test-tools/strace/tests/netlink_route.c

Purpose: provides broad route netlink (`NETLINK_ROUTE`) message decoding coverage for rtnetlink header types, flags, common payload structures, unsupported message families, and newer route objects such as nexthops and interface stats.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `sendto`, `struct nlmsghdr`, `ifinfomsg`, `ifaddrmsg`, `rtmsg`, `ndmsg`, `ndtmsg`, `tcmsg`, `tcamsg`, `ifaddrlblmsg`, `dcbmsg`, `netconfmsg`, `br_port_msg`, `rtgenmsg`, `nhmsg`, `if_stats_msg`, `TEST_NL_ROUTE_`, `TEST_NETLINK_`, and `ifindex_lo`.

Control flow: `main` checks basic type/flag decoding and `NLMSG_DONE`, then runs per-message-family helpers for link, address, route, neighbor, rules, traffic control, actions, prefix fallbacks, neighbor table, ND user options, address labels, DCB, netconf, MDB, route generator messages, interface stats, nexthops, linkprop, VLAN, MDB get, tunnel, and other unsupported/unknown slots. Each structured helper tests short read, exact read, and under-read paths.

State and persistence: sends synthetic rtnetlink messages only. It uses the loopback ifindex for symbolic interface output but does not change links, routes, qdiscs, or netfilter state.

Dependencies and integration points: depends on many Linux rtnetlink UAPI headers and strace xlat tables for route message ids, address families, flags, scopes, protocols, and interface indices. The `TEST_NL_ROUTE_` macro is the integration point for consistent boundary testing.

Risks and edge cases: rtnetlink constants evolve frequently; newer constants may vary by headers. Boundary risks include family-only payloads, unknown families, short reads, unknown message ids, bitmask formatting, and symbolic ifindex resolution.

Test signals: output should show route message names and structured fields for every supported payload, raw/data fallbacks for unsupported messages, unknown comments for gaps, and a clean exit.
