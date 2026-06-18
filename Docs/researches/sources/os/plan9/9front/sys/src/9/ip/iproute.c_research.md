# File Research: sources/os/plan9/9front/sys/src/9/ip/iproute.c

Implements IPv4/IPv6 route storage, lookup, readback, and control parsing.

Key elements:
- Stores routes in bucketed balanced range trees, with separate IPv4 and IPv6 roots.
- Represents destination ranges and optional source-specific ranges.
- Supports route types for interface, unicast, broadcast, multicast, point-to-point, proxy, transparent, and IPv4.
- Provides `addroute`, `delroute`, `flushrouteifc`, `v4lookup`, `v6lookup`, `v4source`, and `v6source`.
- Implements route generation counters and `Routehint` cache validation.
- Parses `/net/iproute` control messages for `add`, `del/remove`, `flush`, and `tag`.
- Formats route table reads with address, mask, gateway, type, tag, interface, source, and source mask.

Dependencies:
- Uses `Ipifc` source selection helpers from `ipifc.c`.
- Uses route structures from `ip.h`.
- Integrates with per-channel route tags through `IPaux`.

Research notes:
- Routes associated with an interface are invalidated by incrementing `ifc->ifcid`.
- A route can be more specific either by destination range or by source range.
- Interface routes are protected from being overwritten by non-interface routes.
