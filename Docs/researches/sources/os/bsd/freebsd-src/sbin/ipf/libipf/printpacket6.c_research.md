# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket6.c

IPv6 packet summary printer.

Key behavior:
- Parses IPv6 header bytes manually.
- Prints direction, interface, version, payload length, flow label, next-header protocol, source/destination addresses, and TCP/UDP ports when payload length permits.

Research notes:
- Avoids reliance on IPv6 header library availability, but does not parse extension headers before TCP/UDP ports.
