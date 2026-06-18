# sources/test-tools/strace/bundled/linux/include/uapi/linux/rtnetlink.h

## Purpose

Defines the core routing netlink ABI for link, address, route, neighbor, rule, traffic-control, multicast database, nexthop, tunnel, VLAN, and statistics messages. strace uses it to decode `NETLINK_ROUTE` message types, common payload structs, attribute headers, multicast groups, and routing flags.

## Important APIs, Types, and Dependencies

Dependencies are `linux/types.h`, `linux/netlink.h`, `linux/if_link.h`, `linux/if_addr.h`, and `linux/neighbour.h`. Message ids run from `RTM_NEWLINK` through route, neighbor, rule, qdisc/class/filter/action, prefix, netconf, MDB, NSID, stats, chain, nexthop, linkprop, VLAN, nexthop bucket, and tunnel families. `struct rtattr` and `RTA_*` macros define generic nested attributes. `struct rtmsg` plus route type, protocol, scope, table, route flags, and `enum rtattr_type_t` describe routes. `struct rtnexthop`, `rtvia`, `rta_cacheinfo`, `rta_session`, `rta_mfc_stats`, `rtgenmsg`, `ifinfomsg`, `prefixmsg`, `tcmsg`, `nduseroptmsg`, and `tcamsg` cover common payloads. The header also exports `RTMGRP_*` legacy groups, `enum rtnetlink_groups`, traffic-control root/action attributes, dump flags, and extended link filters.

## Control Flow, State, and Integration

The ABI is message based: userspace sends netlink requests with a route-netlink message type, base struct, and nested attributes; the kernel replies or multicasts state changes. Persistent state is network namespace routing tables, device/link configuration, addresses, neighbors, qdisc state, bridge VLAN/MDB state, nexthop objects, and tunnel metadata.

## Risks and Test Signals

Risks include broken `RTA_OK`/`RTA_NEXT` length walking, attribute alignment mistakes, message-family number drift, route metric nesting confusion, and old legacy multicast group names overlapping newer group enums. Test signals include decoder tests for every `RTM_*` family, route/nexthop attribute parsing, tc payload parsing with `pkt_sched.h`, multicast group display, and safe unknown attribute handling.
