# File Research: sources/os/plan9/9front/sys/src/9/ip/ip.h

Defines the core types, constants, protocol interfaces, route structures, ARP structures, and function declarations shared by the 9front kernel IP stack.

Key contents:
- Global constants for address lengths, IPv4/IPv6 versions, header sizes, max packet size, route-table sizing, states, and MIB counters.
- Core data structures: `Fs`, `IP`, `Proto`, `Conv`, `Ipifc`, `Iplifc`, `Ipmulti`, `Medium`, `Route`, `Iphash`, `Ipht`, `Translation`, `Arpent`, `Routehint`, `Ndb`.
- Protocol callbacks for connect/announce/bind/state/create/close/receive/control/advice/stats/local/remote/inuse/gc/forward.
- Media callbacks for bind/unbind/bwrite/multicast/address registration/prefix-to-address conversion.
- Routing, ARP, IP auxiliary, interface, ICMP, TCP, BOOTP, and device entry-point declarations.

Important implementation details:
- `Conv` embeds `Iphash`, allowing conversation pointers to be recovered with `iphconv()`.
- `Translation` embeds two `Iphash` structures for forward and backward NAT lookup.
- `Routehint` caches the last route generation and ARP entry for repeated sends.
- `Fs` owns one full IP stack instance, including protocol registry, route roots, ARP cache, self table, NDB, and logs.
- `Ipifc` represents a physical/logical interface binding and contains MTU, medium, MAC, logical addresses, multicast/RA flags, and traffic shaping state.
- `Proto` is the central protocol registration object used by `devip.c`.

Dependencies and integration:
- Included by nearly all files in this group.
- Declares the contracts implemented by `devip.c`, `arp.c`, `ip.c`, `ipaux.c`, `ethermedium.c`, ICMP, IL, GRE, ESP, and interface/routing modules outside this group.

Research notes:
- This header is the architectural map of the networking subsystem.
- It combines user-facing device concepts, packet data-plane concepts, and routing/NAT internals in one shared interface.
