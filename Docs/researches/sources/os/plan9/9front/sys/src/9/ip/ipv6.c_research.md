# File Research: sources/os/plan9/9front/sys/src/9/ip/ipv6.c

Implements IPv6 initialization, output, input forwarding, extension-header handling, fragmentation, and reassembly.

Key elements:
- Initializes IPv6 router-advertisement defaults and neighbor-discovery timing parameters.
- `ipoput6` routes outbound packets, fills IPv6 headers, handles loopback bypass, clamps TCP MSS when forwarding, and fragments local output when needed.
- Refuses intermediate IPv6 fragmentation unless the outgoing interface has `reassemble` enabled.
- `ipiput6` validates incoming packets, forwards routable packets, enforces hop-limit behavior, and dispatches local packets to protocol handlers.
- Handles hop-by-hop/routing/fragment header traversal through `unfraglen`.
- Reassembles IPv6 fragments with overlap trimming, timeout cleanup, and IP_MAX bounds.

Dependencies:
- Uses `iproute.c` lookups, `ipifc.c` local-address checks, `icmpv6` error helpers, and `tcpmssclamp`.
- Uses IPv6 constants and header layouts from `ipv6.h`.

Research notes:
- Forwarding blocks link-local destinations and link-scope multicast.
- Fragment reassembly stores metadata in block base space and concatenates enough state to return a valid packet chain.
- `procopts` is currently a pass-through placeholder.
