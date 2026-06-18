# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/resend.c

This file implements packet replay for `ipresend`.

`dumppacket()` prints summary fields from an IPv4 packet: TOS, fragment offset, length, ID, TTL, protocol, source/destination and ports, and TCP sequence/ack/flags.

`ip_resend()` opens the output device, opens an input packet reader, optionally resolves a fixed gateway MAC, reads packets into an `mb_t`, and either wraps IP packets in Ethernet headers or sends raw captured frames when `OPT_RAW` is set. It computes an IP checksum if absent and sends through `sendip()`.

Important dependencies include `ipsend.h`, `struct ipread` reader callbacks, `arp()`, `chksum()`, and backend `sendip()`.

Implementation notes and risks:
- The branch for no fixed gateway appears to ARP on `gwip` even when `gwip.s_addr` is zero, which is suspicious.
- Ethernet-specific framing is assumed outside raw mode.
- Replay continues past ARP failures for individual packets.
