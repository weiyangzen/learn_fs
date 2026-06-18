# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactivenat.c

Printer for live NAT table entries.

Key behavior:
- Prints NAT type, clone/orphan markers, old/new endpoints, ports, protocol, and direction-specific layout.
- Handles rewrite, outbound map, and inbound redirect forms.
- Verbose mode prints TTL, use count, checksum deltas, hashes, flags, interfaces, byte/packet counters, and IP checksum delta.
- Debug mode prints internal linkage pointers and timer queue state.

Research notes:
- Assumes `getprotobynumber()` succeeds before dereferencing `pproto->p_name`.
