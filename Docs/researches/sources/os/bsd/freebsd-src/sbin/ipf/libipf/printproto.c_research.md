# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printproto.c

Protocol-name printer.

Key behavior:
- For NAT rules, honors aggregate flags such as `tcp/udp`, `tcp`, `udp`, and `icmp`.
- Prints `ip` for protocol zero in NAT context.
- Otherwise prints `protoent` name or numeric protocol.

Research notes:
- NAT context prefers rule flags over the supplied protocol number.
