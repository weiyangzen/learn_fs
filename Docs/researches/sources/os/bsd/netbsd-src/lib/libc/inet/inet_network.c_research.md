# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_network.c

Implements `inet_network`, parsing an Internet network number.

Behavior:
- Supports decimal, octal (`0` prefix), and hex (`0x`) numeric components.
- Parses up to four dot-separated byte components.
- Rejects invalid digits, too many parts, component values over `0xff`, and trailing non-space characters.
- Packs parsed components into a host-order network number.
- Returns `INADDR_NONE` on parse failure.

This is legacy classful IPv4 parsing, not modern CIDR parsing.
