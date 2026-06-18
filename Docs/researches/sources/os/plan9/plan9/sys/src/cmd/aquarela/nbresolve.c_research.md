# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbresolve.c

Resolves NetBIOS names to IP addresses.

Key function:
- `nbnameresolve` checks the remote NetBIOS cache, queries NBNS, caches successful NBNS results by TTL, then falls back to DNS using the name without NetBIOS type byte.

Interactions:
- Used by NetBIOS session connect and direct unique datagram send.

Notable details:
- NBNS is preferred over DNS.
- DNS query uses `/net` and record type `ip`.
