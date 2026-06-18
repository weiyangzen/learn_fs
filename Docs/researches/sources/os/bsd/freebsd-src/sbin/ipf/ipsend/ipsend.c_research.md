# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.c

This is the main `ipsend` command-line packet generator.

It builds a single IPv4 packet from command-line options or delegates to the IP language parser with `-L`. Options set protocol, ICMP type/code/redirect data, TCP/UDP destination port, TCP flags/window, source, gateway, device, fake MTU, fragment flags, and IP options.

`do_icmp()` builds ICMP headers and optional redirect payload fields. `udpcksum()` computes a UDP checksum using a pseudoheader. `send_packets()` opens the output device and delegates to `send_packet()`.

The main path resolves source/destination/gateway, inserts IP options when requested, applies TCP flag characters, prints packet parameters, computes UDP checksums, and sends through either `do_socket()` under `DOSOCKET` or raw packet send routines.

Important dependencies include `ipsend.h`, `ipf.h`, `iplang`, `buildopts()`, `resolve()`, and packet backend functions.

Implementation notes and risks:
- Many options mutate a raw in-memory packet buffer directly.
- IP option insertion reallocates/copies packet data manually.
- The tool is intentionally capable of crafting unusual or malformed packets for firewall testing.
