# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v1trap.c

`ipmon` SNMPv1 trap saver backend.

Key behavior:
- Registers `snmpv1saver`.
- Parses `community address`, opens a connected UDP socket to port 162, and supports IPv4 plus optional IPv6 destination parsing.
- Manually BER-encodes an SNMPv1 enterprise trap for IPFilter enterprise OID `1.3.6.1.4.1.9932`.
- Includes IPFilter version and message text variable bindings.

Research notes:
- Reference-counted contexts share sockets/community strings.
- `writeint()` contains a typo in the 32768 branch divisor (`327678`), also present in v2.
