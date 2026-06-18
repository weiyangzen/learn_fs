# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getport.c

This helper resolves a service/port name into a network-byte-order port.

Without a filter rule context, it tries `getservbyname(name, proto)` and then numeric parsing. With an IPFilter rule context, it handles ambiguous protocol cases:
- If protocol is unspecified, TCP and UDP service mappings must be absent or agree.
- If the rule is TCP/UDP, both TCP and UDP service mappings must exist and match.
- Otherwise it resolves using the rule’s numeric protocol.

Invalid names, out-of-range numeric ports, or ambiguous TCP/UDP mappings return `-1`.
