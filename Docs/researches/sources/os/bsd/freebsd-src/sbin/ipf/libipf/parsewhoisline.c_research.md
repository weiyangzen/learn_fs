# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsewhoisline.c

WHOIS netrange line parser.

Key behavior:
- Searches for `(NET...)` or `(NET6...)` marker.
- Parses IPv4 or IPv6 start/end address ranges after the marker.
- Converts a contiguous range into base address plus mask.
- Rejects non-contiguous masks or addresses not aligned to the derived mask.

Research notes:
- IPv6 support depends on `USE_INET6`.
- IPv4 address/mask fields are stored in `addrfamily_t`.
