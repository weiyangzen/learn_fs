# File Research: sources/os/plan9/9front/sys/src/9/ip/ipifc.c

Implements Plan 9 IP interface management.

Key elements:
- Registers link media types and binds/unbinds `Ipifc` conversations to media.
- Manages logical interface addresses, masks, remote networks, point-to-point routes, proxy routes, and IPv6 autoconf-derived addresses.
- Maintains the `Ipself` cache of local, broadcast, and multicast addresses accepted by the host.
- Adds/removes route-table entries as interface addresses and multicast memberships change.
- Provides source address selection helpers for IPv4 and IPv6.
- Handles `/net/ipifc` control commands: `bind`, `add`, `try`, `del`, `unbind`, `add6`, `del6`, `mtu`, `speed`, `delay`, `reflect`, `reassemble`, and `ra6`.

Dependencies:
- Uses `Medium` implementations such as loopback, pkt, null, and netdev.
- Calls routing APIs from `iproute.c`.
- Uses IPv6 helpers from `ipv6.h` and medium address-resolution hooks.

Research notes:
- Binding a non-loopback medium also binds loopback support for local packet injection.
- The self-address cache is deliberately delayed-free to avoid heavy locking while packets may still reference entries.
- IPv6 source selection prefers global, then ULA, then link-local, while avoiding deprecated/tentative addresses.
