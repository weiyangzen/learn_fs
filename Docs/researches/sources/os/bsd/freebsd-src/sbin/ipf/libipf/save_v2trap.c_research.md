# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v2trap.c

`ipmon` SNMPv2 trap saver backend.

Key behavior:
- Registers `snmpv2saver`.
- Parses `community address`, opens a connected UDP socket to port 162, and supports IPv4 plus optional IPv6 destination parsing.
- Manually BER-encodes an SNMPv2 trap PDU.
- Emits sysUpTime, IPFilter version, and message text variable bindings.

Research notes:
- Structure closely mirrors `save_v1trap.c`.
- Contains unused `server` field in the context struct.
