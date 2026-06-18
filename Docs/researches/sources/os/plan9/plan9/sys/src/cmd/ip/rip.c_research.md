# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rip.c

RIP v1 routing daemon for IPv4 routes.

Key behavior:
- Reads interfaces and existing routes from Plan 9 `/net/iproute`.
- Opens UDP port `rip` in header mode.
- Receives RIP response packets, ignores packets from local interfaces, computes destination/mask/gateway/metric, and considers each route.
- Maintains in-memory route hash with fixed maximum route count.
- Installs better or refreshed routes into `/net/iproute`, unless read-only mode is enabled.
- Periodically broadcasts route tables to selected interfaces/networks.
- Times out non-static routes after 10 minutes.

Integration:
- Uses Plan 9 IP interface discovery via `readipifc()`.
- Uses route control file commands `add` and `delete`.
- Supports alternate net mount via `-x`.

Risks and notes:
- RIP v1 has no authentication and weak routing security.
- Default route is protected from hijacking by comparing against the saved default.
- The “ignore our own messages” loop uses `continue` inside the interface loop, which does not skip the packet as a whole.
