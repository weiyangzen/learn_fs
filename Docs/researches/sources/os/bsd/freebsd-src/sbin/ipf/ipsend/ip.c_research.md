# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ip.c

This file contains low-level packet construction and send helpers for `ipsend`, `iptest`, and `ipresend`.

`chksum()` computes an Internet checksum. `send_ether()` wraps an IP payload in an Ethernet header, ARP-resolves the gateway, and sends through the active backend `sendip()`.

`send_ip()` prepares Ethernet and IPv4 headers, fills defaults for version/id/TTL, resolves source and destination MACs, computes header checksums, and either sends a full packet or fragments it according to the supplied MTU. Fragmentation attempts to copy only copied IP options into later fragments.

`send_tcp()`, `send_udp()`, and `send_icmp()` construct protocol checksums and normalize protocol/header lengths before delegating to `send_ip()`. `send_packet()` dispatches based on `ip_p`.

Important dependencies include `ipsend.h`, ARP backend functions, and platform-specific `sendip()`/`initdevice()` implementations.

Implementation notes and risks:
- Uses static packet buffers and ARP caches, so it is not reentrant.
- Designed for test packet generation, including deliberately malformed packets.
- `send_packet()` contains stray parentheses in return lines in this source, which may depend on historical preprocessing or be dead in some builds.
- Fragmentation comments acknowledge incomplete IP option handling.
