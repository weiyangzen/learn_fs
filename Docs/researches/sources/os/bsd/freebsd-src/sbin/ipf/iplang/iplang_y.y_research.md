# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_y.y

`iplang_y.y` is the yacc grammar and semantic implementation for constructing and sending synthetic IPv4 packets from a textual packet language.

Grammar coverage:
- Top-level `interface`, `arp`, `router`, `send`, and `ipv4` statements.
- Interface attributes: name, MTU, Ethernet address, IPv4 address.
- Send attributes: interface and gateway (`via`).
- ARP entries mapping IPv4 addresses to Ethernet addresses.
- IPv4 fields: protocol, source/destination, offset, version, header length, id, TTL, TOS, checksum, length, and options.
- Nested TCP, UDP, ICMP, and data bodies.
- TCP fields/options: source/destination ports, sequence, ack, offset, urgent pointer, window, checksum, flags, NOP/EOL/MSS/window-scale/timestamp options.
- UDP fields: source/destination ports, length, checksum.
- ICMP types/codes and type-specific payloads for echo, unreachable, redirect, time exceeded, timestamp, info, mask, and parameter problem cases.
- IPv4 options including route, timestamp, security, CIPSO, SATID, SSRR/LSRR, and related historical options.
- Data payloads by length, inline escaped value, or external file.

Implementation model:
- Uses a 66 KiB `ipbuffer` and a linked `aniphdr_t` stack to append nested headers/data.
- `new_header()` appends a header, points it into the current buffer, and grows enclosing IP/UDP lengths.
- `inc_anipheaders()` adjusts lengths for all enclosing headers.
- `end_ipv4`, `end_tcp`, `end_udp`, and `end_icmp` compute checksums and unwind the header stack.
- `packet_done()` optionally hex-dumps the built packet, calls `prep_packet()`, and frees header metadata.
- `prep_packet()` opens the selected device with `initdevice()` and sends with `send_ip()` using selected/default gateway logic.

Notable details and risks:
- Host/service lookups are done with `gethostbyname()`/`getservbyname()`.
- `set_datafile()` refuses packet data exceeding 65535 total bytes.
- TCP/UDP port setters use `"udp"` as the protocol string even on the TCP branch, which looks like a bug in service-name lookup.
- Many semantic errors print messages but continue rather than aborting, so malformed language input can still produce partially built packets.
