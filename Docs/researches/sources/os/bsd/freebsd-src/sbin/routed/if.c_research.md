# File Research: sources/os/bsd/freebsd-src/sbin/routed/if.c

Interface discovery, lifecycle, lookup, health monitoring, and direct-route installation for FreeBSD `routed`.

Key responsibilities:
- Maintains global local/remote interface lists plus address, broadcast, and name hash tables.
- Resolves interfaces by address, name, index, and likely packet ingress network.
- Computes classful/RIPv1 masks, checks destination sanity, duplicate interfaces, and remote-gateway reachability.
- Periodically reads kernel interface state via routing sysctl `NET_RT_IFLIST`.
- Adds, changes, deletes, sickens, and restores interfaces, including aliases and multicast group membership.
- Detects bad/off/disappeared links through interface flags and packet/error counters.
- Installs connected routes, loopback host routes for point-to-point local ends, multihomed host routes, and synthetic RIPv1 network routes.
- Applies configured interface parameters through `get_parms()` and enables RIP/router-discovery state.

Dependencies:
- Uses `defs.h`, `pathnames.h`, routing table helpers, radix walking, router discovery hooks, RIP socket state, kernel routing sockets/sysctls, multicast group socket options, and `/etc/gateways` path constants.

Notable risks:
- Interface deletion recursively removes aliases while walking shared lists, so traversal safety is important.
- Broken/sick state drives route deletion and rediscovery timing; subtle counter wrap or timing bugs can destabilize routes.
- RIPv1 classful/subnet synthesis logic can create or remove daemon routes that differ from kernel route aggregation.
