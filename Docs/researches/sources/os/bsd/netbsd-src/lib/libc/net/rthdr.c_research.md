# File Research: sources/os/bsd/netbsd-src/lib/libc/net/rthdr.c

IPv6 routing-header helper APIs for legacy RFC2292 and RFC3542 interfaces. The RFC2292 functions allocate ancillary-data space, initialize type-0 routing headers, append loose route addresses, report segment counts, return addresses, and report loose-hop flags.

The RFC3542 functions operate directly on routing-header buffers: `inet6_rth_space()`, `inet6_rth_init()`, `inet6_rth_add()`, `inet6_rth_reverse()`, `inet6_rth_segments()`, and `inet6_rth_getaddr()`. Only `IPV6_RTHDR_TYPE_0` is supported, with validation of length parity, segment count, and index bounds.
