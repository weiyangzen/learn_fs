# File Research: sources/os/bsd/freebsd-src/sbin/route/route_netlink.c

Purpose: netlink backend for the FreeBSD `route` command.

Key functions:
- `nl_init_socket()` opens `NETLINK_ROUTE`, attempting to load the `netlink` kernel module if needed.
- `rtmsg_nl_int()` translates route command requests into netlink route messages with destination prefix, table/FIB, gateway, output interface, route flags, metrics, expiration, priority, and weight.
- `rtmsg_nl()` wraps helper setup/teardown around one command.
- `print_getmsg()` and `print_nhop_getmsg()` display route lookup results, including next-hop view when `-o` is used.
- `monitor_nl()` subscribes to link, neighbor, nexthop, IPv4, and IPv6 route/address multicast groups and prints events.
- `print_nlmsg_route()`, `print_nlmsg_link()`, `print_nlmsg_addr()`, and `print_nlmsg_neigh()` format monitor events.
- `flushroutes_fib_nl()` dumps routes for a table/family and deletes gateway routes through `flushroute_one()`.

Integration: called from `route.c` through declared backend functions. Uses FreeBSD simple netlink (`snl_*`) route parsers and writers. Reuses `route.c` formatting helpers `routename()`, `netname()`, `printb()`, and `routeflags`.

Risk notes: route socket and netlink semantics are translated manually, especially around prefixes, gateways, link-local scope IDs, and route flags. Some monitor output is informational rather than a stable machine format. `flushroute_one()` contains unreachable warning code after an early return in one error branch.
