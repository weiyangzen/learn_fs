# File Research: sources/os/bsd/freebsd-src/sbin/routed/rdisc.c

ICMP Router Discovery Protocol support for client solicitation, router advertisement, default-route selection, and multicast group management.

Key responsibilities:
- Defines local ICMP router advertisement and solicitation packet layouts.
- Opens and configures a raw ICMP socket for router discovery.
- Joins/leaves all-hosts and all-routers multicast groups per interface based on supplier/client mode and policy.
- Switches the daemon to supplier mode when multiple RIP interfaces make route supply necessary.
- Maintains a fixed table of discovered routers with interface, gateway, lifetime, and preference.
- Ages discovered routers, removes stale/bad defaults, chooses the best default route, and toggles RIP on/off depending on router discovery success.
- Sends router advertisements as supplier and solicitations as client with randomized timers.
- Parses incoming advertisements and solicitations, validates packet shape, source/interface, address size, lifetime, preferences, and reachable gateways.
- Responds to valid solicitations with unicast advertisements.

Dependencies:
- Uses raw sockets, ICMP/IP headers, multicast group socket options, route-table default-route operations, interface state, timers, and RIP socket control.

Notable risks:
- Deliberately departs from RFC 1256 in aging bad routers quickly to avoid black holes.
- Preference conversion uses signed/unsigned transforms and metric biasing; errors can invert route choice.
- Packet interface attribution is limited without `SO_PASSIFNAME`, especially for source address zero solicitations.
