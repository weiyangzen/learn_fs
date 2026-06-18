<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.c -->
# sources/test-tools/strace/src/netlink_route.c

Purpose: dispatches `NETLINK_ROUTE` payloads to RTM message-specific route decoders.

Important APIs/types/functions: `decode_netlink_route`, local `decode_family`, `route_decoders`, and `DECL_NETLINK_ROUTE_DECODER` function pointers.

Control flow: skips `NLMSG_DONE`, fetches the first family byte, computes `nlmsg_type - RTM_BASE`, and calls a registered decoder for link, address, route, neighbor, rule, qdisc/class/filter/action, netconf, mdb, nsid, stats, nexthop, and related RTM messages. Unknown types fall back to printing family plus raw data.

State and persistence behavior: no persistent state.

Dependencies and integration points: invoked by `netlink.c`; depends on `netlink_route.h`, `<linux/rtnetlink.h>`, `addrfams`, and route decoder implementations in other strace source files.

Risks: dispatcher coverage must track new RTM message numbers. Incorrect index arithmetic or missing entries lead to generic output for otherwise decodable route messages.

Test signals: route netlink tests for representative RTM families, unknown RTM types, short payloads, `NLMSG_DONE`, and correct fallback family rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.c -->
