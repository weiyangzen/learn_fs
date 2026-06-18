# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_poolnode.c

Pool node add/delete helper.

Key behavior:
- Copies address, mask, negation/info flag, TTL, and node name into a local `ip_pool_node_t`.
- Uses `SIOCLOOKUPADDNODE` or `SIOCLOOKUPDELNODE`.
- On error, prints the pool name and address/mask.

Research notes:
- Mask string buffer is only eight bytes, enough for IPv4 dotted masks only because IPv6 suppresses mask text.
