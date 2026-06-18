# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6ionames.c

IPv6 extension-header name table.

Key behavior:
- Compiled under `USE_INET6`.
- Defines `v6ionames[]` mapping protocol numbers to match bits and text names for hopopts, ipv6, routing, frag, ESP, AH, none, dstopts, and mobility.

Research notes:
- All lengths are zero because these are extension-header identifiers, not fixed option lengths.
