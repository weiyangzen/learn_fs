<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.h -->
# sources/test-tools/strace/src/netlink_route.h

Purpose: declares the route-netlink decoder signature and all route message decoder entry points used by the route dispatcher.

Important APIs/types/functions: `DECL_NETLINK_ROUTE_DECODER` and extern declarations for link, address, route, neighbor, rule, tc, action, dcb, netconf, bridge mdb, nsid, stats, cache report, and nexthop decoders.

Control flow: no runtime flow; macro-generated prototypes enforce a consistent `(tcp, nlmsghdr, family, addr, len)` contract.

State and persistence behavior: no state.

Dependencies and integration points: consumed by `netlink_route.c` and implemented across route-related decoder files.

Risks: adding a route decoder requires both this declaration and `route_decoders` registration. Signature mismatch is compile-time visible.

Test signals: full strace build plus route-netlink dispatch tests that reference each declared decoder family.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.h -->
