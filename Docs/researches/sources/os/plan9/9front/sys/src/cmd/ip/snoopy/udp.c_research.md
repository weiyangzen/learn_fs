# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/udp.c

This snoopy module decodes and filters UDP packets.

Key behavior:
- Filters support source port (`s`), destination port (`d`), and either port (`a`/`sd`).
- Muxes DNS, BOOTP, 9P, RTP, and RTCP.
- RTP/RTCP use `ANYPORT`; selecting them in a filter sets a temporary default payload protocol.
- Prints source/destination ports, checksum, and UDP length.
- Resets the temporary default protocol to `dump` after each packet.

Research notes:
- The global `defproto` is mutable during filtering, so RTP/RTCP interpretation depends on filter path.
